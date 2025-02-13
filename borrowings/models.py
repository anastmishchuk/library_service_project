from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError

from books.models import Book
from library_service_project import settings


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="borrowings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings"
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(expected_return_date__gt=models.F("borrow_date")),
                name="check_expected_after_borrow",
            )
        ]

    def return_book(self) -> None:
        """Updates actual_return_date and return the book to inventory."""
        if self.actual_return_date:
            raise ValidationError("This book has already been returned")
        self.actual_return_date = timezone.now().date()
        self.book.inventory += 1
        self.book.save()
        self.save()

    def __str__(self):
        return f"Book {self.book.title} borrowed from {self.borrow_date} to {self.expected_return_date}"
