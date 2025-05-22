from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from unittest.mock import patch, MagicMock

from payment_service.models import Payment
from payment_service.serializers import PaymentSerializer
from payment_service.permissions import IsOwnerOrAdmin, IsAdminOrReadOnly
from borrowings.models import Borrowing
from books.models import Book
from django.contrib.auth import get_user_model

User = get_user_model()


class PaymentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com",
            password="password",
            first_name="Test",
            last_name="User"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            daily_fee=Decimal("10.00"),
            inventory=5,
            cover="HARD"
        )
        self.borrowing = Borrowing.objects.create(
            expected_return_date=timezone.now() + timezone.timedelta(days=5),
            book=self.book,
            user=self.user
        )

    def test_payment_creation(self):
        payment = Payment.objects.create(
            borrowing=self.borrowing,
            session_id="test_session_id",
            session_url="https://test.com/session",
            money_to_pay=Decimal("50.00"),
            status=Payment.Status.PENDING,
            type=Payment.Type.PAYMENT
        )
        self.assertEqual(payment.borrowing, self.borrowing)
        self.assertEqual(payment.session_id, "test_session_id")
        self.assertEqual(payment.money_to_pay, Decimal("50.00"))
        self.assertEqual(payment.status, Payment.Status.PENDING)
        self.assertEqual(payment.type, Payment.Type.PAYMENT)

    def test_payment_str(self):
        payment = Payment.objects.create(
            borrowing=self.borrowing,
            session_id="test_session_id",
            session_url="https://test.com/session",
            money_to_pay=Decimal("50.00")
        )
        expected_str = f"Payment {payment.status} for borrowing {self.borrowing.id}"
        self.assertEqual(str(payment), expected_str)


class PaymentSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com",
            password="password",
            first_name="Test",
            last_name="User"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            daily_fee=Decimal("10.00"),
            inventory=5,
            cover="HARD"
        )
        self.borrowing = Borrowing.objects.create(
            expected_return_date=timezone.now() + timezone.timedelta(days=5),
            book=self.book,
            user=self.user
        )
        self.payment = Payment.objects.create(
            borrowing=self.borrowing,
            session_id="test_session_id",
            session_url="https://test.com/session",
            money_to_pay=Decimal("50.00")
        )

    def test_payment_serializer(self):
        serializer = PaymentSerializer(self.payment)
        data = serializer.data
        self.assertEqual(data["id"], self.payment.id)
        self.assertEqual(data["status"], self.payment.status)
        self.assertEqual(data["type"], self.payment.type)
        self.assertEqual(data["borrowing"], self.borrowing.id)
        self.assertEqual(data["session_url"], self.payment.session_url)
        self.assertEqual(data["session_id"], self.payment.session_id)
        self.assertEqual(Decimal(data["money_to_pay"]), self.payment.money_to_pay)


class PaymentViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@test.com",
            password="password",
            first_name="Test",
            last_name="User"
        )
        self.admin_user = User.objects.create_superuser(
            email="admin@test.com",
            password="adminpass"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            daily_fee=Decimal("10.00"),
            inventory=5,
            cover="HARD"
        )
        self.borrowing = Borrowing.objects.create(
            expected_return_date=timezone.now() + timezone.timedelta(days=5),
            book=self.book,
            user=self.user
        )
        self.payment = Payment.objects.create(
            borrowing=self.borrowing,
            session_id="test_session_id",
            session_url="https://test.com/session",
            money_to_pay=Decimal("50.00")
        )

    def test_payment_list_unauthorized(self):
        response = self.client.get(reverse("payment-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_payment_list_authorized(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("payment-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_payment_list_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(reverse("payment-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_payment_detail_unauthorized(self):
        response = self.client.get(
            reverse("payment-detail", kwargs={"pk": self.payment.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_payment_detail_authorized(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse("payment-detail", kwargs={"pk": self.payment.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.payment.id)

    def test_payment_detail_wrong_user(self):
        other_user = User.objects.create_user(
            email="other@test.com",
            password="password",
            first_name="Other",
            last_name="User"
        )
        self.client.force_authenticate(user=other_user)
        response = self.client.get(
            reverse("payment-detail", kwargs={"pk": self.payment.id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_payment_delete_regular_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(
            reverse("payment-detail", kwargs={"pk": self.payment.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_payment_delete_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(
            reverse("payment-detail", kwargs={"pk": self.payment.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class PaymentPermissionsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com",
            password="password",
            first_name="Test",
            last_name="User"
        )
        self.admin_user = User.objects.create_superuser(
            email="admin@test.com",
            password="adminpass"
        )
        self.other_user = User.objects.create_user(
            email="other@test.com",
            password="password",
            first_name="Other",
            last_name="User"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            daily_fee=Decimal("10.00"),
            inventory=5,
            cover="HARD"
        )
        self.borrowing = Borrowing.objects.create(
            expected_return_date=timezone.now() + timezone.timedelta(days=5),
            book=self.book,
            user=self.user
        )
        self.payment = Payment.objects.create(
            borrowing=self.borrowing,
            session_id="test_session_id",
            session_url="https://test.com/session",
            money_to_pay=Decimal("50.00")
        )
        self.owner_permission = IsOwnerOrAdmin()
        self.admin_permission = IsAdminOrReadOnly()

    def test_owner_permission_owner(self):
        request = type('Request', (), {'user': self.user})()
        self.assertTrue(
            self.owner_permission.has_object_permission(request, None, self.payment)
        )

    def test_owner_permission_admin(self):
        request = type('Request', (), {'user': self.admin_user})()
        self.assertTrue(
            self.owner_permission.has_object_permission(request, None, self.payment)
        )

    def test_owner_permission_other_user(self):
        request = type('Request', (), {'user': self.other_user})()
        self.assertFalse(
            self.owner_permission.has_object_permission(request, None, self.payment)
        )

    def test_admin_permission_safe_method(self):
        request = type('Request', (), {'user': self.user, 'method': 'GET'})()
        self.assertTrue(
            self.admin_permission.has_permission(request, None)
        )

    def test_admin_permission_unsafe_method_admin(self):
        request = type('Request', (), {'user': self.admin_user, 'method': 'DELETE'})()
        self.assertTrue(
            self.admin_permission.has_permission(request, None)
        )

    def test_admin_permission_unsafe_method_user(self):
        request = type('Request', (), {'user': self.user, 'method': 'DELETE'})()
        self.assertFalse(
            self.admin_permission.has_permission(request, None)
        )

    def test_admin_permission_anonymous(self):
        request = type('Request', (), {'user': None, 'method': 'GET'})()
        self.assertFalse(
            self.admin_permission.has_permission(request, None)
        )


class PaymentProcessingTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="user@test.com",
            password="password",
            first_name="Test",
            last_name="User"
        )
        self.admin_user = User.objects.create_superuser(
            email="admin@test.com",
            password="adminpass"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            daily_fee=Decimal("10.00"),
            inventory=5,
            cover="HARD"
        )
        self.borrowing = Borrowing.objects.create(
            expected_return_date=timezone.now() + timezone.timedelta(days=5),
            book=self.book,
            user=self.user
        )

    @patch('payment_service.stripe_service.stripe.checkout.Session.create')
    def test_start_payment_unauthorized(self, mock_create):
        response = self.client.post(
            reverse("start-payment", kwargs={"borrowing_id": self.borrowing.id})
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('payment_service.stripe_service.stripe.checkout.Session.create')
    def test_start_payment_authorized(self, mock_create):
        mock_session = MagicMock()
        mock_session.id = "test_session_id"
        mock_session.url = "https://test.com/session"
        mock_create.return_value = mock_session

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("start-payment", kwargs={"borrowing_id": self.borrowing.id})
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("payment_id", response.data)
        self.assertIn("checkout_url", response.data)
        self.assertEqual(response.data["checkout_url"], "https://test.com/session")

    @patch('payment_service.stripe_service.stripe.checkout.Session.create')
    def test_start_payment_wrong_user(self, mock_create):
        other_user = User.objects.create_user(
            email="other@test.com",
            password="password",
            first_name="Other",
            last_name="User"
        )
        self.client.force_authenticate(user=other_user)
        response = self.client.post(
            reverse("start-payment", kwargs={"borrowing_id": self.borrowing.id})
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('payment_service.stripe_service.stripe.checkout.Session.retrieve')
    def test_payment_success(self, mock_retrieve):
        payment = Payment.objects.create(
            borrowing=self.borrowing,
            session_id="test_session_id",
            session_url="https://test.com/session",
            money_to_pay=Decimal("50.00")
        )
        mock_session = MagicMock()
        mock_session.payment_status = "paid"
        mock_retrieve.return_value = mock_session

        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse("payment-success", kwargs={"payment_id": payment.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "success")
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.PAID)

    @patch('payment_service.stripe_service.stripe.checkout.Session.retrieve')
    def test_payment_success_pending(self, mock_retrieve):
        payment = Payment.objects.create(
            borrowing=self.borrowing,
            session_id="test_session_id",
            session_url="https://test.com/session",
            money_to_pay=Decimal("50.00")
        )
        mock_session = MagicMock()
        mock_session.payment_status = "pending"
        mock_retrieve.return_value = mock_session

        self.client.force_authenticate(user=self.user)
        response = self.client.get(
            reverse("payment-success", kwargs={"payment_id": payment.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "pending")
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.Status.PENDING)

    def test_payment_cancel(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("payment-cancel"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "cancelled") 