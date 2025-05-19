from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status

from borrowings.models import Borrowing
from books.models import Book
from django.contrib.auth import get_user_model
from borrowings.serializers import BorrowingReadSerializer

User = get_user_model()

class BorrowingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="user@test.com", password="password")
        self.book = Book.objects.create(title="Test Book", author="Author")

    def test_borrowing_clean_validation(self):
        now = timezone.now()
        borrowing = Borrowing(
            borrow_date=now,
            expected_return_date=now,
            actual_return_date=now,
            book=self.book,
            user=self.user,
        )
        with self.assertRaises(ValidationError) as cm:
            borrowing.clean()
        self.assertIn("Expected return date must be after borrow date.", str(cm.exception))

        borrowing.expected_return_date = now + timezone.timedelta(days=1)
        borrowing.actual_return_date = now - timezone.timedelta(days=1)
        with self.assertRaises(ValidationError) as cm:
            borrowing.clean()
        self.assertIn("Actual return date cannot be before borrow date.", str(cm.exception))

    def test_borrowing_str(self):
        borrowing = Borrowing.objects.create(
            expected_return_date=timezone.now() + timezone.timedelta(days=5),
            book=self.book,
            user=self.user
        )
        expected_str = f"{self.user.email} borrowed {self.book.title} on {borrowing.borrow_date}"
        self.assertEqual(str(borrowing), expected_str)

class BorrowingSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="user@test.com", password="password")
        self.book = Book.objects.create(title="Test Book", author="Author")
        self.borrowing = Borrowing.objects.create(
            expected_return_date=timezone.now() + timezone.timedelta(days=5),
            book=self.book,
            user=self.user
        )

    def test_borrowing_read_serializer(self):
        serializer = BorrowingReadSerializer(self.borrowing)
        data = serializer.data
        self.assertEqual(data["id"], self.borrowing.id)
        self.assertIn("borrow_date", data)
        self.assertIn("expected_return_date", data)
        self.assertIn("actual_return_date", data)
        self.assertIn("book", data)
        self.assertEqual(data["book"]["title"], self.book.title)

class BorrowingViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", email="user@test.com", password="password")
        self.book = Book.objects.create(title="Test Book", author="Author")
        self.borrowing = Borrowing.objects.create(
            expected_return_date=timezone.now() + timezone.timedelta(days=5),
            book=self.book,
            user=self.user
        )

    def test_borrowing_list(self):
        response = self.client.get("/borrowings/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, list)
        self.assertGreaterEqual(len(response.data), 1)
        borrowing_data = response.data[0]
        self.assertIn("id", borrowing_data)
        self.assertIn("borrow_date", borrowing_data)
        self.assertIn("expected_return_date", borrowing_data)
        self.assertIn("actual_return_date", borrowing_data)
        self.assertIn("book", borrowing_data)

    def test_borrowing_detail(self):
        response = self.client.get(f"/borrowings/{self.borrowing.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.borrowing.id)
