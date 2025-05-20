from rest_framework import status

from books.models import Book
from books.serializers import BookReadSerializer
from books.tests.test_base import (
    BaseApiTestCase,
    BOOKS_URL,
    sample_book,
    detail_book_url,
    sample_book_payload
)


class BookTests(BaseApiTestCase):
    def setUp(self):
        super().setUp()
        self.authenticate_user()

    def test_model_str_methods(self):
        book = sample_book()
        self.assertEqual(str(book), "Sample Book by John Doe")

    def test_list_books(self):
        sample_book(title="Book 1")
        sample_book(title="Book 2")

        res_list = self.client.get(BOOKS_URL)

        books = Book.objects.all()
        serializer_list = BookReadSerializer(books, many=True)

        for book in res_list.data:
            daily_fee = book["daily_fee"]
            self.assertTrue(daily_fee.startswith("$"))

        self.assertEqual(len(res_list.data), 2)
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertEqual(res_list.data, serializer_list.data)

    def test_detail_books(self):
        book = sample_book()

        res_detail = self.client.get(detail_book_url(book.id))
        daily_fee = res_detail.data["daily_fee"]

        serializer_detail = BookReadSerializer(book)

        self.assertTrue(daily_fee.startswith("$"))
        self.assertEqual(res_detail.status_code, status.HTTP_200_OK)
        self.assertEqual(res_detail.data, serializer_detail.data)

    def test_forbidden_create_book(self):
        payload = sample_book_payload()

        res = self.client.post(BOOKS_URL, payload)

        self.assertEqual(Book.objects.count(), 0)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_forbidden_update_book(self):
        book = sample_book()
        payload = sample_book_payload(title="Test Title")

        res_put = self.client.put(detail_book_url(book.id), payload)
        res_patch = self.client.patch(detail_book_url(book.id), payload)

        book.refresh_from_db()

        self.assertNotEqual(book.title, "Test Title")
        self.assertEqual(res_put.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(res_patch.status_code, status.HTTP_403_FORBIDDEN)

    def test_forbidden_delete_book(self):
        book = sample_book()

        res = self.client.delete(detail_book_url(book.id))

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Book.objects.filter(id=book.id).exists())
