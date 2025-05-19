from rest_framework import viewsets
from payment_service.models import Payment
from payment_service.serializers import PaymentSerializer
from payment_service.permissions import IsOwnerOrAdmin


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsOwnerOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(borrowing__user=user)
