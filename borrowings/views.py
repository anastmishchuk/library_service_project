from django.utils import timezone
from rest_framework.decorators import action

from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from borrowings.models import Borrowing
from borrowings.serializers import (BorrowingSerializer,
                                    BorrowingDetailSerializer)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        Admins can see all borrowings, others see only their own.
        """
        queryset = Borrowing.objects.all() if self.request.user.is_staff else Borrowing.objects.filter(
            user=self.request.user)

        # Apply active filter
        queryset = self.filter_by_active(queryset)

        # Filter by user_id if the user is an admin
        if self.request.user.is_staff:
            user_id = self.request.query_params.get("user_id")
            if user_id is not None:
                queryset = queryset.filter(user_id=user_id)

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer

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

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated], url_path="return")
    def return_borrowing(self, request, pk=None):
        """
        This function check if borrowing has already been returned,
        mark the borrowing as returned and increase the inventory of the associated book by 1.
        """

        borrowing = self.get_object()

        if borrowing.actual_return_date is not None:
            return Response(
                {"detail": "This borrowing has already been returned."},
                status=status.HTTP_400_BAD_REQUEST
            )

        borrowing.actual_return_date = timezone.now()
        borrowing.save()

        book = borrowing.book
        book.inventory += 1
        book.save()

        return Response(
            {"detail": "Borrowing returned successfully."},
            status=status.HTTP_200_OK
        )
