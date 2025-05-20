from rest_framework import status

from books.models import Book
from books.tests.test_base import (
    BaseApiTestCase,
    BOOKS_URL,
    sample_book,
    detail_book_url,
    sample_book_payload
)


class BookAdminTests(BaseApiTestCase):
    def setUp(self):
        super().setUp()
        self.authenticate_user(is_admin=True)

    def test_create_book_success(self):
        payload = sample_book_payload(
            title="New Admin Book",
            daily_fee=10,
            inventory=5
        )
        res = self.client.post(BOOKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)

        book = Book.objects.get(id=res.data["id"])
        self.assertEqual(book.title, "New Admin Book")
        self.assertEqual(book.daily_fee, 10)
        self.assertEqual(book.inventory, 5)
        self.assertEqual(res.data["daily_fee"], "10.00")

    def test_create_book_duplicate_title_same_author(self):
        sample_book(title="Unique Book", author="John Doe")

        payload = sample_book_payload(title="Unique Book", author="John Doe")
        res = self.client.post(BOOKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", res.data)

    def test_update_book_success(self):
        book = sample_book(daily_fee=10, inventory=5)

        payload = sample_book_payload(
            title="Updated Book",
            inventory=20,
            daily_fee=15
        )
        res_put = self.client.put(detail_book_url(book.id), payload)

        self.assertEqual(res_put.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertEqual(book.title, "Updated Book")
        self.assertEqual(book.inventory, 20)
        self.assertEqual(book.daily_fee, 15)

        payload = {"title": "Partially Updated Book"}
        res_patch = self.client.patch(detail_book_url(book.id), payload)

        self.assertEqual(res_patch.status_code, status.HTTP_200_OK)
        book.refresh_from_db()
        self.assertEqual(book.title, "Partially Updated Book")
        self.assertEqual(book.daily_fee, 15)

    def test_delete_book(self):
        book = sample_book()

        res = self.client.delete(detail_book_url(book.id))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Book.objects.filter(id=book.id).exists())

    def test_update_book_missing_fields(self):
        book = sample_book()

        payload = {"title": ""}
        res_patch = self.client.patch(detail_book_url(book.id), payload)
        self.assertEqual(res_patch.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("title", res_patch.data)

        payload = {"daily_fee": ""}
        res_patch = self.client.patch(detail_book_url(book.id), payload)
        self.assertEqual(res_patch.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("daily_fee", res_patch.data)

    def test_create_book_invalid_data(self):
        payload = sample_book_payload(inventory=-5)
        res = self.client.post(BOOKS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("inventory", res.data)

        payload = sample_book_payload(daily_fee=0)
        res = self.client.post(BOOKS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("daily_fee", res.data)

        payload = sample_book_payload(daily_fee=-1)
        res = self.client.post(BOOKS_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("daily_fee", res.data)

    def test_update_book_invalid_data(self):
        book = sample_book()

        payload = {"inventory": -10}
        res_put = self.client.put(detail_book_url(book.id), payload)
        self.assertEqual(res_put.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("inventory", res_put.data)

        payload = {"daily_fee": 0}
        res_patch = self.client.patch(detail_book_url(book.id), payload)
        self.assertEqual(res_patch.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("daily_fee", res_patch.data)

        payload = {"daily_fee": -5}
        res_patch = self.client.patch(detail_book_url(book.id), payload)
        self.assertEqual(res_patch.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("daily_fee", res_patch.data)
