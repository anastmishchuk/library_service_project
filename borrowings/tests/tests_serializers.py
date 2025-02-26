from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer
from books.models import Book
from users.models import User


class BorrowingSerializerTests(TestCase):
    """
    Test case for BorrowingSerializer, ensuring correct behavior
    when serializing and deserializing borrowing data.
    """
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass"
        )
        self.superuser = User.objects.create_superuser(
            email="testadmin@example.com",
            password="testpassadmin"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=5,
            daily_fee=4.00)
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=7),
        )
        self.url_list = reverse("borrowings:borrowings-list")
        self.url_detail = reverse(
            "borrowings:borrowings-detail", args=[self.borrowing.id]
        )
        self.url_return = reverse(
            "borrowings:borrowings-return-borrowing",
            args=[self.borrowing.id]
        )

    def test_borrowing_serializer_valid_data(self):
        """
        Test that the BorrowingSerializer correctly validates valid input data.
        """
        data = {
            "book": self.book.id,
            "expected_return_date": timezone.now().date() + timezone.timedelta(days=5)
        }
        serializer = BorrowingSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_borrowing_serializer_book_not_available(self):
        """
        Test that the BorrowingSerializer prevents borrowing if the book's inventory is zero.
        """
        self.book.inventory = 0
        self.book.save()
        data = {
            "book": self.book,
            "expected_return_date": timezone.now().date() + timezone.timedelta(days=5)
        }
        serializer = BorrowingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("book", serializer.errors)

    def test_borrowing_serializer_create(self):
        """
        Test creating a borrowing instance.
        """
        self.client.force_authenticate(user=self.user)
        data = {
            "book": self.book.id,
            "borrow_date": str(
                timezone.now().date() + timezone.timedelta(days=1)
            ),
            "expected_return_date": str(
                timezone.now().date() + timezone.timedelta(days=10)
            )
        }
        response = self.client.post(self.url_list, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 4)
        borrowing = Borrowing.objects.get(id=response.data["id"])
        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(borrowing.book, self.book)

    def test_borrowing_list_serializer(self):
        """
        Test retrieving a list of borrowings.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.borrowing.id)

    def test_borrowing_detail_serializer(self):
        """
        Test retrieving a specific borrowing instance.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.borrowing.id)

    def test_borrowing_return_serializer(self):
        """
        Test returning a book by admin.
        """
        self.client.force_authenticate(user=self.superuser)
        response = self.client.post(self.url_return)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.borrowing.refresh_from_db()
        self.assertIsNotNone(self.borrowing.actual_return_date)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 6)

    def test_return_borrowing_already_returned(self) -> None:
        """
        Test that attempting to return an already returned book fails.
        """
        self.client.force_authenticate(user=self.superuser)
        self.borrowing.actual_return_date = timezone.now().date()
        self.borrowing.save()

        response = self.client.post(self.url_return)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(
            response.data["error"],
            "This book has already been returned"
        )

    def test_admin_see_all_borrowings(self) -> None:
        """
        Test that only the admin can see all borrowings.
        """
        self.client.force_authenticate(user=self.superuser)
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
