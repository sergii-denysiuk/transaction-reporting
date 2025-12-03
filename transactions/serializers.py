from rest_framework import serializers

from .models import Transaction


class TransactionIngestSerializer(serializers.Serializer):
    transaction_type = serializers.ChoiceField(
        choices=Transaction.TransactionType.choices
    )
    status = serializers.ChoiceField(
        choices=Transaction.Status.choices,
    )
    transaction_number = serializers.CharField(max_length=64)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    year = serializers.IntegerField(min_value=1900, max_value=2100)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "transaction_type",
            "transaction_number",
            "amount",
            "status",
            "year",
        ]


class TransactionReportSerializer(serializers.Serializer):
    row_field = serializers.CharField()
    column_fields = serializers.ListField(child=serializers.CharField())
    data = serializers.ListField()
    column_totals = serializers.ListField()
    grand_total = serializers.CharField()
