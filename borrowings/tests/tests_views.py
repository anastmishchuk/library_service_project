from datetime import timedelta
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from borrowings.models import Borrowing
from books.models import Book

User = get_user_model()


class BorrowingViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password_user"
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="password_admin"
        )

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=3,
            daily_fee=2.00,
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=5),
        )

        self.url_list = reverse("borrowings:borrowings-list")
        self.url_detail = reverse(
            "borrowings:borrowings-detail", args=[self.borrowing.pk]
        )
        self.client.force_authenticate(user=self.user)

    def test_create_borrowing(self):
        """
        Test creating a new borrowing by user.
        """
        data = {
            "book": self.book.id,
            "borrow_date": str((timezone.now() + timedelta(days=1)).date()),
            "expected_return_date": str((timezone.now() + timedelta(days=1)).date() + timedelta(days=10)),
        }
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url_list, data)
        if response.status_code != status.HTTP_201_CREATED:
            print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        borrowing = Borrowing.objects.get(id=response.data["id"])
        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(borrowing.book, self.book)

    def test_list_borrowings(self):
        """
        Test retrieving the borrowing list.
        """
        response = self.client.get(self.url_list)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)

    def test_retrieve_borrowing(self):
        """
        Test retrieving a single borrowing's details.
        """
        response = self.client.get(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["id"], self.borrowing.id)


class BorrowingViewSetReturnTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@example.com",
            password="password_user"
        )
        self.admin = User.objects.create_superuser(
            email="admin@example.com",
            password="password_admin"
        )

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=3,
            daily_fee=2.00,
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=timezone.now().date(),
            expected_return_date=timezone.now().date() + timezone.timedelta(days=5),
        )

        self.url_return = reverse(
            "borrowings:borrowings-return-borrowing", args=[self.borrowing.pk]
        )
        self.client.force_authenticate(user=self.admin)

    def test_return_borrowing(self):
        """
        Test that an admin can return a borrowed book.
        """
        response = self.client.post(self.url_return, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.borrowing.refresh_from_db()
        self.assertIsNotNone(self.borrowing.actual_return_date)

    def test_return_borrowing_already_returned(self):
        """
        Test that attempting to return an already returned book fails.
        """
        self.client.force_authenticate(user=self.admin)

        self.borrowing.actual_return_date = timezone.now()
        self.borrowing.save()

        response = self.client.post(self.url_return)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"],
            "This book has already been returned"
        )

    def test_non_admin_cannot_return_borrowing(self):
        """
        Test that a regular user cannot return a book.
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url_return, content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
