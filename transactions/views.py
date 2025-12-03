from django.db.models import QuerySet
from rest_framework import generics

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionListView(generics.ListAPIView):
    """List raw transactions with optional filtering.

    Supports filtering by transaction_type, status, and year via
    query parameters combined with AND logic.
    """

    serializer_class = TransactionSerializer

    def get_queryset(self) -> QuerySet[Transaction]:
        queryset = Transaction.objects.all().order_by("-year", "transaction_number")

        transaction_type = self.request.query_params.get("transaction_type")
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)

        status = self.request.query_params.get("status")
        if status:
            queryset = queryset.filter(status=status)

        year = self.request.query_params.get("year")
        if year and year.isdigit():
            queryset = queryset.filter(year=int(year))

        return queryset
