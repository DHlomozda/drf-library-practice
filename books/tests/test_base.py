from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from books.models import Book

User = get_user_model()

BOOKS_URL = reverse("books:book-list")


def detail_book_url(book_id):
    return reverse("books:book-detail", args=[book_id])


def get_book_defaults(**params):
    defaults = {
        "title": "Sample Book",
        "author": "John Doe",
        "cover": "HARD",
        "inventory": 5,
        "daily_fee": 10.00,
    }
    defaults.update(params)
    return defaults


def sample_book(**params) -> Book:
    return Book.objects.create(**get_book_defaults(**params))


def sample_book_payload(**params) -> dict:
    return get_book_defaults(**params)


class BaseApiTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def authenticate_user(self, is_admin=False):
        self.user = User.objects.create_user(
            email="admin@example.com" if is_admin else "user@example.com",
            password="test_password123",
            first_name="Test",
            last_name="User",
            is_staff=is_admin
        )
        self.client.force_authenticate(self.user)
