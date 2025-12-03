from django.db.models import QuerySet
from rest_framework import generics

from ..models import Transaction
from ..serializers import TransactionSerializer
from .base import TransactionFilterMixin, TransactionFilterSchema, TransactionPagination


class TransactionListView(TransactionFilterMixin, generics.ListAPIView):
    """List raw transactions with optional filtering.
    Supports filtering by transaction_type, status, and year via
    query parameters combined with AND logic. Results are paginated
    using page and page_size query parameters.
    """

    schema = TransactionFilterSchema()
    serializer_class = TransactionSerializer
    pagination_class = TransactionPagination

    def get_base_queryset(self) -> QuerySet[Transaction]:
        return Transaction.objects.all().order_by("-year", "transaction_number")

    def get_queryset(self) -> QuerySet[Transaction]:
        return self.get_filtered_queryset()
