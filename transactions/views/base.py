from django.conf import settings
from django.db.models import QuerySet
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.schemas.openapi import AutoSchema

from ..models import Transaction


class TransactionFilterSchema(AutoSchema):
    def get_filter_parameters(self, path, method):
        params = super().get_filter_parameters(path, method)

        if method.lower() != "get":
            return params

        # Only add custom filter params; rely on DRF pagination for page/page_size
        params.extend(
            [
                {
                    "name": "transaction_type",
                    "in": "query",
                    "required": False,
                    "description": "Filter by transaction type.",
                    "schema": {
                        "type": "string",
                        "enum": list(Transaction.TransactionType.values),
                    },
                },
                {
                    "name": "status",
                    "in": "query",
                    "required": False,
                    "description": "Filter by payment status.",
                    "schema": {
                        "type": "string",
                        "enum": list(Transaction.Status.values),
                    },
                },
                {
                    "name": "year",
                    "in": "query",
                    "required": False,
                    "description": "Filter by year (e.g. 2024). Non-numeric values are ignored.",
                    "schema": {"type": "integer"},
                },
            ]
        )
        return params


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
