from django.test import TestCase
from django.utils import timezone
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
from django.utils.timezone import now
from borrowings.models import Borrowing
from books.models import Book
from django.contrib.auth import get_user_model
from borrowings.serializers import BorrowingReadSerializer, BorrowingCreateSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import translation

User = get_user_model()


class BorrowingModelTest(TestCase):
    def setUp(self):
        translation.activate('en-us')
        self.user = User.objects.create_user(first_name="Test",
                                             last_name="User",
                                             email="user@test.com",
                                             password="password",
                                             is_staff=True)
        self.book = Book.objects.create(title="Test Book",
                                        author="Author",
                                        inventory=10,
                                        daily_fee=1.5,
                                        cover="HARD")

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
        self.assertEqual(str(cm.exception.messages[0]),
                         "Expected return date must be after borrow date.")

        borrowing.expected_return_date = now + timezone.timedelta(days=1)
        borrowing.actual_return_date = now - timezone.timedelta(days=1)
        with self.assertRaises(ValidationError) as cm:
            borrowing.clean()
        self.assertEqual(str(cm.exception.messages[0]),
                         "Actual return date cannot be before borrow date.")

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
        self.user = User.objects.create_user(first_name="Test",
                                             last_name="User",
                                             email="user@test.com",
                                             password="password",
                                             is_staff=True)
        self.book = Book.objects.create(title="Test Book",
                                        author="Author",
                                        inventory=10,
                                        daily_fee=1.5,
                                        cover="HARD")
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
        self.user = User.objects.create_user(first_name="Test",
                                             last_name="User",
                                             email="user@test.com",
                                             password="password",
                                             is_staff=True)
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
        self.book = Book.objects.create(title="Test Book",
                                        author="Author",
                                        inventory=10,
                                        daily_fee=1.5,
                                        cover="HARD"
                                        )
        self.borrowing = Borrowing.objects.create(
            expected_return_date=timezone.now() + timezone.timedelta(days=5),
            book=self.book,
            user=self.user
        )

    def test_borrowing_list(self):
        response = self.client.get("/api/borrowings/")
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
        response = self.client.get(f"/api/borrowings/{self.borrowing.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.borrowing.id)


class BorrowingCreateSerializerTestCase(TestCase):
    def setUp(self):
        self.book_available = Book.objects.create(
            title="Test Book",
            inventory=5,
            daily_fee=2.50,
            author="John Doe",
            cover="HARD"
        )
        self.book_unavailable = Book.objects.create(
            title="Unavailable Book",
            inventory=1,
            daily_fee=1.50,
            author="Jane Smith",
            cover="SOFT"
        )
        self.book_unavailable.inventory = 0
        self.book_unavailable.save(update_fields=["inventory"])

        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            password="testpassword",
            is_staff=True
        )

    def test_validate_expected_return_date_future(self):
        from rest_framework.exceptions import ValidationError
        serializer = BorrowingCreateSerializer()

        valid_date = now() + timezone.timedelta(days=1)
        validated_date = serializer.validate_expected_return_date(valid_date)
        self.assertEqual(validated_date, valid_date)

        invalid_date = now() - timezone.timedelta(days=1)
        with self.assertRaises(ValidationError) as context:
            serializer.validate_expected_return_date(invalid_date)
        self.assertEqual(str(context.exception.detail[0]),
                         "Expected return date must be in the future.")

    def test_validate_inventory_book_available(self):
        data = {
            "book": self.book_available.id,
            "expected_return_date": now() + timezone.timedelta(days=1),
        }
        serializer = BorrowingCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_validate_inventory_book_unavailable(self):
        data = {
            "book": self.book_unavailable.id,
            "expected_return_date": now() + timezone.timedelta(days=1),
        }
        serializer = BorrowingCreateSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("book", serializer.errors)
        self.assertEqual(
            serializer.errors["book"][0],
            "Sorry, the book is currently unavailable for borrowing"
        )
