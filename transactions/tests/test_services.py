import dataclasses

import pytest
from django.db.models import QuerySet

from transactions.models import Transaction
from transactions.services import (
    ReportDimension,
    TransactionReportRequest,
    TransactionReportService,
)


@pytest.mark.django_db
class TestTransactionReportService:

    @classmethod
    def _build_qs(cls, sample_transactions: list[Transaction]) -> QuerySet[Transaction]:
        return Transaction.objects.filter(id__in=[t.id for t in sample_transactions])

    def test_row_only_aggregation(self, sample_transactions):
        """Group only by transaction_type (rows only, no explicit column dimensions)."""
        qs = self._build_qs(sample_transactions)
        request = TransactionReportRequest(
            row_field=ReportDimension.TRANSACTION_TYPE,
            column_fields=[],
        )
        result = TransactionReportService.build_report(qs, request)

        assert dataclasses.asdict(result) == {
            "row_field": "transaction_type",
            "column_fields": [],
            "data": [
                {
                    "row_key": {"transaction_type": "bill"},
                    "cells": [
                        {
                            "column_key": {},
                            "total_amount": "50.00",
                        }
                    ],
                    "row_total": "50.00",
                },
                {
                    "row_key": {"transaction_type": "invoice"},
                    "cells": [
                        {
                            "column_key": {},
                            "total_amount": "175.00",
                        }
                    ],
                    "row_total": "175.00",
                },
            ],
            "column_totals": [
                {
                    "column_key": {},
                    "total_amount": "225.00",
                }
            ],
            "grand_total": "225.00",
        }

    def test_row_and_single_column(self, sample_transactions):
        """Group by transaction_type (rows) and status (single column dimension)."""
        qs = self._build_qs(sample_transactions)
        request = TransactionReportRequest(
            row_field=ReportDimension.TRANSACTION_TYPE,
            column_fields=[ReportDimension.STATUS],
        )
        result = TransactionReportService.build_report(qs, request)

        assert dataclasses.asdict(result) == {
            "row_field": "transaction_type",
            "column_fields": ["status"],
            "data": [
                {
                    "row_key": {"transaction_type": "bill"},
                    "cells": [
                        {
                            "column_key": {"status": "unpaid"},
                            "total_amount": "50.00",
                        }
                    ],
                    "row_total": "50.00",
                },
                {
                    "row_key": {"transaction_type": "invoice"},
                    "cells": [
                        {
                            "column_key": {"status": "paid"},
                            "total_amount": "100.00",
                        },
                        {
                            "column_key": {"status": "unpaid"},
                            "total_amount": "75.00",
                        },
                    ],
                    "row_total": "175.00",
                },
            ],
            "column_totals": [
                {
                    "column_key": {"status": "unpaid"},
                    "total_amount": "125.00",
                },
                {
                    "column_key": {"status": "paid"},
                    "total_amount": "100.00",
                },
            ],
            "grand_total": "225.00",
        }

    def test_row_and_two_columns(self, sample_transactions):
        """Group by transaction_type (rows), and (year, status) as columns."""
        qs = self._build_qs(sample_transactions)
        request = TransactionReportRequest(
            row_field=ReportDimension.TRANSACTION_TYPE,
            column_fields=[ReportDimension.YEAR, ReportDimension.STATUS],
        )
        result = TransactionReportService.build_report(qs, request)

        assert dataclasses.asdict(result) == {
            "row_field": "transaction_type",
            "column_fields": ["year", "status"],
            "data": [
                {
                    "row_key": {"transaction_type": "bill"},
                    "cells": [
                        {
                            "column_key": {"year": 2024, "status": "unpaid"},
                            "total_amount": "50.00",
                        }
                    ],
                    "row_total": "50.00",
                },
                {
                    "row_key": {"transaction_type": "invoice"},
                    "cells": [
                        {
                            "column_key": {"year": 2024, "status": "paid"},
                            "total_amount": "100.00",
                        },
                        {
                            "column_key": {"year": 2024, "status": "unpaid"},
                            "total_amount": "75.00",
                        },
                    ],
                    "row_total": "175.00",
                },
            ],
            "column_totals": [
                {
                    "column_key": {"year": 2024, "status": "unpaid"},
                    "total_amount": "125.00",
                },
                {
                    "column_key": {"year": 2024, "status": "paid"},
                    "total_amount": "100.00",
                },
            ],
            "grand_total": "225.00",
        }

    @pytest.mark.django_db
    def test_no_matching_rows(self):
        qs = Transaction.objects.none()
        request = TransactionReportRequest(
            row_field=ReportDimension.TRANSACTION_TYPE,
            column_fields=[ReportDimension.STATUS],
        )
        result = TransactionReportService.build_report(qs, request)

        assert dataclasses.asdict(result) == {
            "row_field": "transaction_type",
            "column_fields": ["status"],
            "data": [],
            "column_totals": [],
            "grand_total": "0",
        }
