from rest_framework import serializers

from borrowings.models import Borrowing
from books.serializers import BookSerializer
from users.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = "__all__"


class BorrowingListSerializer(BorrowingSerializer):
    book_id = serializers.CharField(
        source="book.id"
    )
    user_id = serializers.CharField(
        source="user.id"
    )

    class Meta:
        model = Borrowing
        fields = ("id",
                  "borrow_date",
                  "expected_return_date",
                  "actual_return_date",
                  "book_id",
                  "user_id")


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(many=False, read_only=True)
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user"
        )
