from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from borrowings.models import Borrowing
from books.models import Book
from django.contrib.auth import get_user_model
from borrowings.serializers import BorrowingReadSerializer


User = get_user_model()


class BorrowingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com",
            password="password",
            first_name="Test",
            last_name="User"
        )
        self.book = Book.objects.create(title="Test Book", author="Author", inventory=1, daily_fee=10, cover="HARD")

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
        self.user = User.objects.create_user(
            email="user@test.com",
            password="password",
            first_name="Test",
            last_name="User"
        )
        self.book = Book.objects.create(title="Test Book", author="Author", inventory=1, daily_fee=10, cover="HARD")
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
        self.user = User.objects.create_user(
            email="user@test.com",
            password="password",
            first_name="Test",
            last_name="User"
        )
        self.book = Book.objects.create(title="Test Book", author="Author", inventory=1, daily_fee=10, cover="HARD")
        self.borrowing = Borrowing.objects.create(
            expected_return_date=timezone.now() + timezone.timedelta(days=5),
            book=self.book,
            user=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_borrowing_list(self):
        url = reverse("borrowings:borrowing-list")
        response = self.client.get(url)
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
        url = reverse("borrowings:borrowing-detail", args=[self.borrowing.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.borrowing.id)


class BorrowingReturnTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@test.com",
            password="password",
            first_name="Test",
            last_name="User"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            inventory=1,
            daily_fee=10,
            cover="HARD"
        )
        self.borrowing = Borrowing.objects.create(
            expected_return_date=timezone.now() + timezone.timedelta(days=5),
            book=self.book,
            user=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_return_book_success(self):
        url = reverse("borrowings:borrowing-return-book", args=[self.borrowing.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Book has been successfully returned.")
        
        self.borrowing.refresh_from_db()
        self.assertIsNotNone(self.borrowing.actual_return_date)
        
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 2)

    def test_return_book_already_returned(self):
        url = reverse("borrowings:borrowing-return-book", args=[self.borrowing.id])
        self.client.post(url)
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["error"], "This book has already been returned.")

    def test_return_book_unauthorized(self):
        self.client.force_authenticate(user=None)
        url = reverse("borrowings:borrowing-return-book", args=[self.borrowing.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
