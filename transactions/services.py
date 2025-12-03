from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Any

from django.db.models import QuerySet, Sum

from .models import Transaction


class ReportDimension(str, Enum):
    TRANSACTION_TYPE = "transaction_type"
    STATUS = "status"
    YEAR = "year"

    @classmethod
    def values(cls) -> list[str]:
        return [member.value for member in cls]


@dataclass(frozen=True)
class TransactionReportRequest:
    row_field: ReportDimension
    column_fields: list[ReportDimension]


@dataclass(frozen=True)
class TransactionReportResult:
    row_field: str
    column_fields: list[str]
    data: list[dict]
    column_totals: list[dict]
    grand_total: str


class TransactionReportService:
    """Service responsible for building aggregated transaction reports."""

    @classmethod
    def build_report(
        cls,
        queryset: QuerySet[Transaction],
        request: TransactionReportRequest,
    ) -> TransactionReportResult:
        """Aggregates transaction amounts into a pivot-style structure:
        it groups records by the chosen row and column fields,
        calculates the summed amount for each group, and then computes row summaries,
        column summaries, and a grand total across all transactions.
        """
        row_field = request.row_field.value
        column_fields = [field.value for field in request.column_fields]

        group_by: list[str] = [row_field, *column_fields]
        aggregates = (
            queryset.values(*group_by)
            .annotate(total_amount=Sum("amount"))
            .order_by(*group_by)
        )

        rows: dict[Any, dict] = {}
        column_totals_numeric: dict[tuple, Decimal] = {}
        grand_total_numeric: Decimal = Decimal("0")
        for agg in aggregates:
            amount: Decimal = agg["total_amount"] or Decimal("0")

            # Row handling
            row_value = agg[row_field]
            if row_value not in rows:
                rows[row_value] = {
                    "row_key": {row_field: row_value},
                    "cells_by_col_key": {},
                    "row_total_numeric": Decimal("0"),
                }
            row_entry = rows[row_value]
            row_entry["row_total_numeric"] += amount

            # Column / cell handling
            column_key_tuple = (
                tuple(agg[field] for field in column_fields) if column_fields else ()
            )
            cells_by_col_key = row_entry["cells_by_col_key"]
            if column_key_tuple not in cells_by_col_key:
                column_key = (
                    {field: agg[field] for field in column_fields}
                    if column_fields
                    else {}
                )
                cells_by_col_key[column_key_tuple] = {
                    "column_key": column_key,
                    "total_amount_numeric": Decimal("0"),
                }
            cells_by_col_key[column_key_tuple]["total_amount_numeric"] += amount

            # Column totals
            column_totals_numeric[column_key_tuple] = (
                column_totals_numeric.get(column_key_tuple, Decimal("0")) + amount
            )

            # Grand total
            grand_total_numeric += amount

        data_rows: list[dict] = []
        for row_entry in rows.values():
            cells: list[dict] = [
                {
                    "column_key": cell["column_key"],
                    "total_amount": str(cell["total_amount_numeric"]),
                }
                for cell in row_entry["cells_by_col_key"].values()
            ]
            data_rows.append(
                {
                    "row_key": row_entry["row_key"],
                    "cells": cells,
                    "row_total": str(row_entry["row_total_numeric"]),
                }
            )

        column_totals_list: list[dict] = []
        for col_key_tuple, total in column_totals_numeric.items():
            column_key = (
                {column_fields[i]: col_key_tuple[i] for i in range(len(column_fields))}
                if column_fields
                else {}
            )
            column_totals_list.append(
                {
                    "column_key": column_key,
                    "total_amount": str(total),
                }
            )

        return TransactionReportResult(
            row_field=row_field,
            column_fields=column_fields,
            data=data_rows,
            column_totals=column_totals_list,
            grand_total=str(grand_total_numeric),
        )
