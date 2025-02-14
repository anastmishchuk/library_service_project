from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from books.models import Book
from books.serializers import BookSerializer

BOOKS_URL = reverse("books:book-list")


def detail_url(book_id: int) -> str:
    """Returns the detail URL for a book."""
    return reverse("books:book-detail", args=[book_id])


class PublicBookTests(TestCase):
    """Tests for public access to the book API."""

    def setUp(self) -> None:
        """Set up the API client for test."""
        self.client = APIClient()

    def test_retrieve_books_ordered_by_title(self) -> None:
        """Test retrieving a list of books ordered by title."""
        Book.objects.create(
            title="Hunger Games",
            author="Suzanne Collins",
            cover="SOFT",
            inventory=15,
            daily_fee=Decimal("2.00"),
        )
        Book.objects.create(
            title="Me Before You",
            author="Jojo Moyes",
            cover="HARD",
            inventory=12,
            daily_fee=Decimal("1.50"),
        )

        res = self.client.get(f"{BOOKS_URL}?ordering=title")

        books = Book.objects.all().order_by("title")
        serializer = BookSerializer(books, many=True)

        self.assertEqual(res.data, serializer.data)

    def test_create_book_unauthorized(self):
        payload = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "HARD",
            "inventory": 7,
            "daily_fee": Decimal("2.50"),
        }
        res = self.client.post(BOOKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(
            Book.objects.filter(title="Test Book").exists()
        )


class AdminBookTests(TestCase):
    """Tests for admin access to the book API."""

    def setUp(self) -> None:
        """Set up the API client and admin user for tests."""
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="password123",
        )
        self.client.force_authenticate(self.admin_user)
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=10,
            daily_fee=Decimal("2.00"),
        )
        self.book_url = f"/api/books/{self.book.id}/"

    def test_create_book_as_admin(self):
        payload = {
            "title": "New Book",
            "author": "New Author",
            "cover": "SOFT",
            "inventory": 5,
            "daily_fee": Decimal("2.50"),
        }
        res = self.client.post(BOOKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        book = Book.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(getattr(book, key), payload[key])

    def test_delete_book_as_admin(self):
        response = self.client.get(self.book_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        delete_response = self.client.delete(self.book_url)
        self.assertEqual(
            delete_response.status_code, status.HTTP_204_NO_CONTENT
        )

        response_after_delete = self.client.get(self.book_url)
        self.assertEqual(
            response_after_delete.status_code, status.HTTP_404_NOT_FOUND
        )