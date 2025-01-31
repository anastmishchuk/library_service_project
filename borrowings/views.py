from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
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

