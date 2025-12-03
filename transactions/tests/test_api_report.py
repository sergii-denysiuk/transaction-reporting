import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestTransactionReportAPI:
    def test_happy_path(self, client, sample_transactions):
        """Happy-path GET should return a pivoted report with expected totals.

        Detailed aggregation logic is covered by TransactionReportService tests;
        here we just assert that the endpoint is wired correctly and returns
        a compatible shape and expected high-level values.
        """
        url = reverse("transaction-report")
        response = client.get(
            url,
            {
                "row_field": "transaction_type",
                "column_fields": "status",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # Shape
        assert data["row_field"] == "transaction_type"
        assert data["column_fields"] == ["status"]
        assert isinstance(data["data"], list)
        assert isinstance(data["column_totals"], list)

        # A couple of key business expectations (aligned with fixtures)
        assert data["grand_total"] == "225.00"

        rows = {row["row_key"]["transaction_type"]: row for row in data["data"]}
        assert rows["invoice"]["row_total"] == "175.00"  # 100 + 75
        assert rows["bill"]["row_total"] == "50.00"

    def test_validation_errors(self, client, sample_transactions):
        url = reverse("transaction-report")

        # Missing row_field
        resp = client.get(url)
        assert resp.status_code == 400

        # Invalid row_field
        resp = client.get(url, {"row_field": "foo"})
        assert resp.status_code == 400

        # Invalid column field
        resp = client.get(
            url,
            {
                "row_field": "status",
                "column_fields": "year,foo",
            },
        )
        assert resp.status_code == 400

        # Duplicate column fields
        resp = client.get(
            url,
            {
                "row_field": "status",
                "column_fields": "year,year",
            },
        )
        assert resp.status_code == 400

    def test_filters_are_applied_before_aggregation(self, client, sample_transactions):
        url = reverse("transaction-report")
        response = client.get(
            url,
            {
                "row_field": "transaction_type",
                "column_fields": "status",
                "status": "unpaid",
            },
        )

        assert response.status_code == 200
        data = response.json()

        rows = {row["row_key"]["transaction_type"]: row for row in data["data"]}
        assert rows["invoice"]["row_total"] == "75.00"
        assert rows["bill"]["row_total"] == "50.00"
        assert data["grand_total"] == "125.00"
