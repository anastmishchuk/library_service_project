from datetime import date
from rest_framework import serializers

from borrowings.models import Borrowing
from books.models import Book


class BookBorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "daily_fee",
        )


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = "__all__"

    def validate(self, data):
        borrow_date = date.today()
        expected_return_date = data.get("expected_return_date")

        if expected_return_date < borrow_date:
            raise serializers.ValidationError(
                "Expected return date should be later than borrow date."
            )

        return data


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookBorrowingSerializer(read_only=True)

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
