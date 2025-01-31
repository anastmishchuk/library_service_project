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
        book = data.get("book")

        if expected_return_date < borrow_date:
            raise serializers.ValidationError(
                "Expected return date should be later than borrow date."
            )
        if book and book.inventory <= 0:
            raise serializers.ValidationError(
                f"The book '{book.title}' is not available for borrowing."
            )

        return data

    def create(self, validated_data):
        book = validated_data["book"]

        # Decrease the book inventory by 1
        book.inventory -= 1
        book.save()

        # Create the borrowing instance
        return super().create(validated_data)


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
