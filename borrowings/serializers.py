from datetime import date
from rest_framework import serializers

from borrowings.models import Borrowing
from books.serializers import BookSerializer
from users.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and validating Borrowing instances.
    """
    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        ]
        read_only_fields = [
            "borrow_date",
            "actual_return_date",
            "user",
        ]

    def validate(self, data):
        """
        Custom validation for Borrowing creation:
        - Ensures expected return date is not in the past.
        - Checks if the book is available in inventory.
        """
        borrow_date = date.today()
        expected_return_date = data.get("expected_return_date")
        book = data.get("book")

        if expected_return_date is not None and expected_return_date < borrow_date:
            raise serializers.ValidationError(
                "Expected return date should be later than borrow date."
            )
        if book and book.inventory <= 0:
            raise serializers.ValidationError(
                f"The book '{book.title}' is not available for borrowing."
            )

        return data

    def create(self, validated_data):
        """
        Custom logic for borrowing creation -
        decreases the book inventory by 1 upon borrowing.
        """
        book = validated_data["book"]

        # Decrease the book inventory by 1
        book.inventory -= 1
        book.save()

        # Create the borrowing instance
        return super().create(validated_data)


class BorrowingListSerializer(BorrowingSerializer):
    """
    Serializer for listing borrowings.
    Lists borrowings with slug fields for book title and user email.
    """

    book = serializers.SlugRelatedField(slug_field="title", read_only=True)
    user = serializers.SlugRelatedField(slug_field="email", read_only=True)


class BorrowingDetailSerializer(BorrowingSerializer):
    """
    Serializer for detailed borrowing view.
    Includes full nested representations of book and user.
    """
    book = BookSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user"
        ]
        read_only_fields = ["actual_return_date",]


class BorrowingReturnSerializer(BorrowingSerializer):
    """
    Serializer for handling book return.
    Calls the `return_book` method on the instance.
    """
    class Meta:
        model = Borrowing
        fields = []

    def return_borrowing(self) -> None:
        self.instance.return_book()
