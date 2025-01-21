from django.db import models

from books.models import Book
from library_service_project import settings


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField()
    book_id = models.ForeignKey(
        Book, on_delete=models.CASCADE
    )
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-borrow_date"]
