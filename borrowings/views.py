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
        if self.request.user.is_staff:
            return Borrowing.objects.all()
        return Borrowing.objects.filter(user=self.request.user)

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
