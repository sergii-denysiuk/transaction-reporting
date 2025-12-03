from django.conf import settings
from django.db.models import QuerySet
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination

from ..models import Transaction


class TransactionPagination(PageNumberPagination):
    max_page_size = settings.PAGINATION_MAX_PAGE_SIZE
    page_size = settings.PAGINATION_PAGE_SIZE
    page_size_query_param = "page_size"


class TransactionFilterMixin(generics.GenericAPIView):
    """Mixin providing common transaction filtering logic.
    Expects the subclass to implement ``get_base_queryset`` and will apply
    the same filters as the list and report endpoints based on query params.

    This mixin subclasses DRF's GenericAPIView so that ``request`` and
    other view attributes are available without additional hacks.
    """

    def get_base_queryset(self) -> QuerySet[Transaction]:
        raise NotImplementedError("Subclasses must implement get_base_queryset().")

    def get_filtered_queryset(self) -> QuerySet[Transaction]:
        queryset = self.get_base_queryset()

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
