from django.test import TestCase
from django.contrib.auth import get_user_model


class UserModelTests(TestCase):
    """Test for the custom User model"""

    def test_create_user(self):
        """Test regular user creation"""
        user = get_user_model()
        new_user = user.objects.create_user(
            email="testuser@example.com",
            password="testpass123",
            first_name="Test",
            last_name="User",
        )
        self.assertEqual(new_user.email, "testuser@example.com")
        self.assertTrue(new_user.check_password("testpass123"))
        self.assertFalse(new_user.is_staff)
        self.assertFalse(new_user.is_superuser)

    def test_create_superuser(self):
        """Test admin user creation"""

        user = get_user_model()
        superuser = user.objects.create_superuser(
            email="admin@example.com",
            password="admin122345",
            first_name="Admin",
            last_name="User",
        )
        self.assertEqual(superuser.email, "admin@example.com")
        self.assertTrue(superuser.check_password("admin122345"))
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
