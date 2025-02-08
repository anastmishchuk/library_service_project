from django.db import models

from books.models import Book
from library_service_project import settings


class Borrowing(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
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

    def __str__(self):
        return f"ID - {self.id} ({self.borrow_date} - {self.expected_return_date})"
