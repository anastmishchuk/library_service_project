from rest_framework import viewsets

from books.permissions import IsAdminOrReadOnly
from borrowings.models import Borrowing
from borrowings.serializers import (BorrowingSerializer,
                                    BorrowingListSerializer,
                                    BorrowingDetailSerializer)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all().select_related(
        "book", "user"
    )
    serializer_class = BorrowingSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer
