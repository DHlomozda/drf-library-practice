from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id',
            'status',
            'type',
            'borrowing',
            'session_url',
            'session_id',
            'money_to_pay',
            'created_at'
        ]
        read_only_fields = ['created_at']
