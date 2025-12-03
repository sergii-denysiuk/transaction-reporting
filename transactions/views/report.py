from django.db.models import QuerySet
from rest_framework import generics, status
from rest_framework.response import Response

from ..models import Transaction
from ..serializers import TransactionReportSerializer
from ..services import (
    ReportDimension,
    TransactionReportRequest,
    TransactionReportService,
)
from .base import TransactionFilterMixin, TransactionFilterSchema


class TransactionReportSchema(TransactionFilterSchema):
    def get_filter_parameters(self, path, method):
        params = super().get_filter_parameters(path, method)
        if method.lower() != "get":
            return params

        params.extend(
            [
                {
                    "name": "row_field",
                    "in": "query",
                    "required": True,
                    "description": "Column to group by.",
                    "schema": {
                        "type": "string",
                        "enum": sorted(ReportDimension.values()),
                    },
                },
                {
                    "name": "column_fields",
                    "in": "query",
                    "required": False,
                    "description": "Optional comma-separated list from transaction_type,status,year.",
                    "schema": {"type": "string"},
                },
            ]
        )
        return params


class TransactionReportView(TransactionFilterMixin, generics.GenericAPIView):
    """Returns a pre-aggregated, pivot-style report of transactions.
    Use this endpoint when you need totals grouped by a chosen row dimension
    (for example, transaction_type or status) and optional column dimensions,
    All monetary values are summed with Decimal and returned as strings.

    Filters on `transaction_type`, `status`, and `year` are applied **before** the aggregation
    logic, so they affect which transactions are counted in the report.
    """

    schema = TransactionReportSchema()
    serializer_class = TransactionReportSerializer

    def get_base_queryset(self) -> QuerySet[Transaction]:
        return Transaction.objects.all()

    def get(self, request, *args, **kwargs):
        row_field_str = self.request.query_params.get("row_field")
        if not row_field_str:
            return Response(
                {"detail": "row_field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        allowed = set(ReportDimension.values())
        if row_field_str not in allowed:
            return Response(
                {
                    "detail": f"Invalid row_field '{row_field_str}'. Must be one of {sorted(allowed)}."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw_column_fields = self.request.query_params.get("column_fields", "")
        column_field_strs = (
            [_p for part in raw_column_fields.split(",") if (_p := part.strip())]
            if raw_column_fields
            else []
        )

        for field in column_field_strs:
            if field not in allowed:
                return Response(
                    {
                        "detail": f"Invalid column field '{field}'. Must be one of {sorted(allowed)}."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if len(column_field_strs) != len(set(column_field_strs)):
            return Response(
                {"detail": "Duplicate fields are not allowed in column_fields."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        report_request = TransactionReportRequest(
            row_field=ReportDimension(row_field_str),
            column_fields=[ReportDimension(field) for field in column_field_strs],
        )
        qs = self.get_filtered_queryset()
        service = TransactionReportService()
        result = service.build_report(qs, report_request)
        serializer = self.get_serializer(
            {
                "row_field": result.row_field,
                "column_fields": result.column_fields,
                "data": result.data,
                "column_totals": result.column_totals,
                "grand_total": result.grand_total,
            }
        )
        return Response(serializer.data)
