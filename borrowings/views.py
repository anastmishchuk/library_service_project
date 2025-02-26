from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.decorators import action

from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer
)


class BorrowingViewSet(viewsets.ModelViewSet):
    """
        ViewSet for managing borrowings.

        - Admin users can view all borrowings.
        - Regular users can only see their own borrowings.
        - Borrowings can be filtered by user ID and active status.
        - Provides an endpoint for returning a borrowed item (admin only).
        """

    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Retrieve borrowings based on user permissions.

        - Admin users see all borrowings.
        - Regular users see only their own borrowings.
        - Supports filtering by `user_id` (admin only).
        - Supports filtering by active status.
        """
        queryset = Borrowing.objects.all() if self.request.user.is_staff else Borrowing.objects.filter(
            user=self.request.user)

        queryset = self.filter_by_active(queryset)

        if self.request.user.is_staff:
            user_id = self.request.query_params.get("user_id")
            if user_id is not None:
                queryset = queryset.filter(user_id=user_id)

        return queryset

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the action.
        """
        if self.action == "list":
            return BorrowingListSerializer
        elif self.action == "retrieve":
            return BorrowingDetailSerializer
        elif self.action == "return_borrowing":
            return BorrowingReturnSerializer
        return BorrowingSerializer

    def create(self, request, *args, **kwargs):
        """Creates a new borrowing instance.

        Borrowings can only be created via the `/api/borrowings/` endpoint,
        not on specific borrowing instances (`/api/borrowings/<id>/`).
        """
        if self.action != "create":
            return Response(
                {"detail": "You cannot create a borrowing on this endpoint."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Prevents updating borrowings via PUT or PATCH requests."""
        return Response(
            {"detail": "Updating borrowings is not allowed."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def perform_create(self, serializer: ModelSerializer) -> None:
        """
        Saves a new borrowing, setting the user to
        the currently authenticated user.
        """
        serializer.save(user=self.request.user)

    def filter_by_active(self, queryset):
        """
        Filter the borrowings queryset to only include active borrowings
        (i.e., those that have not been returned yet).
        """
        is_active = self.request.query_params.get("is_active")

        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active.lower() == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)

        return queryset

    @extend_schema(
            summary="Return borrowing",
            description="Mark a borrowing as returned. "
                        "This action is available only to admin users.",
            request=BorrowingReturnSerializer,
            responses={
                200: OpenApiResponse(
                    response=dict,
                    description="The book was successfully returned"
                ),
                400: OpenApiResponse(
                    response=dict,
                    description="This book has already been returned"
                ),
            },
        )
    @action(detail=True, methods=["POST"], permission_classes=[IsAdminUser])
    def return_borrowing(self, request: Request, pk: str = None) -> Response:
        """
        Returns a borrowed book.

        - Checks if the book has already been returned.
        - If not, marks the borrowing as returned.
        - Increases the book's inventory count by 1.
        - Only accessible by admin users.
        """
        borrowing = self.get_object()

        if borrowing.actual_return_date is not None:
            return Response(
                {"error": "This book has already been returned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = BorrowingReturnSerializer(instance=borrowing, data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            serializer.return_borrowing()
            return Response({"message": "The book was successfully returned"})
        except ValidationError:
            return Response(
                {"error": "This book has already been returned"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def get_user_borrowings(self, request):
        """Get borrowings by user ID and filter by active status."""
        user_id = request.query_params.get("user_id")
        is_active = request.query_params.get("is_active")

        queryset = self.queryset.filter(user_id=user_id) if user_id else self.queryset

        if is_active is not None:
            is_active = is_active.lower() == "true"
            queryset = queryset.filter(actual_return_date__isnull=is_active)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
