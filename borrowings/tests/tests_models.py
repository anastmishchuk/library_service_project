from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from books.models import Book
from borrowings.models import Borrowing


class BorrowingModelTests(TestCase):
    """
    Test case for the Borrowing model.
    """
    def setUp(self):
        self.user = get_user_model().objects.create_user(email="testuser@example.com", password="testpass")
        self.book = Book.objects.create(title="Test Book", inventory=5, daily_fee=2.50)
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            expected_return_date=timezone.now().date() + timezone.timedelta(days=7)
        )

    def test_borrowing_creation(self):
        """
        Test that a borrowing instance is created correctly.
        """
        self.assertEqual(self.borrowing.book, self.book)
        self.assertEqual(self.borrowing.user, self.user)
        self.assertIsNotNone(self.borrowing.borrow_date)
        self.assertIsNone(self.borrowing.actual_return_date)

    def test_return_book(self):
        """
        Test returning a book.
        """
        self.borrowing.return_book()
        self.assertIsNotNone(self.borrowing.actual_return_date)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 6)

    def test_return_book_already_returned(self):
        """
        Test that returning a book that has already been returned raises a ValidationError.
        """
        self.borrowing.return_book()
        with self.assertRaises(ValidationError):
            self.borrowing.return_book()
