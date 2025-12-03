import pytest
from django.urls import reverse

from .models import Transaction


@pytest.fixture
def sample_transactions() -> list[Transaction]:
    """Create a small, varied set of transactions for API tests."""

    tx1 = Transaction.objects.create(
        transaction_type=Transaction.TransactionType.INVOICE,
        status=Transaction.Status.PAID,
        transaction_number="INV-1",
        amount="100.00",
        year=2024,
    )
    tx2 = Transaction.objects.create(
        transaction_type=Transaction.TransactionType.BILL,
        status=Transaction.Status.UNPAID,
        transaction_number="BILL-1",
        amount="50.00",
        year=2023,
    )
    tx3 = Transaction.objects.create(
        transaction_type=Transaction.TransactionType.INVOICE,
        status=Transaction.Status.UNPAID,
        transaction_number="INV-2",
        amount="75.00",
        year=2024,
    )
    return [tx1, tx2, tx3]


@pytest.mark.django_db
class TestTransactionListAPI:
    def test_list_all_transactions(self, client, sample_transactions):
        url = reverse("transaction-list")
        response = client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == len(sample_transactions)

        # Ensure expected keys are present
        item = data[0]
        for key in [
            "id",
            "transaction_type",
            "transaction_number",
            "amount",
            "status",
            "year",
        ]:
            assert key in item

    def test_filter_by_transaction_type(self, client, sample_transactions):
        url = reverse("transaction-list")
        response = client.get(url, {"transaction_type": "invoice"})

        assert response.status_code == 200
        data = response.json()
        assert {item["transaction_number"] for item in data} == {"INV-1", "INV-2"}

    def test_filter_by_status(self, client, sample_transactions):
        url = reverse("transaction-list")
        response = client.get(url, {"status": "unpaid"})

        assert response.status_code == 200
        data = response.json()
        assert {item["transaction_number"] for item in data} == {"BILL-1", "INV-2"}

    def test_filter_by_year(self, client, sample_transactions):
        url = reverse("transaction-list")
        response = client.get(url, {"year": "2023"})

        assert response.status_code == 200
        data = response.json()
        assert {item["transaction_number"] for item in data} == {"BILL-1"}

    def test_combined_filters_and_logic(self, client, sample_transactions):
        url = reverse("transaction-list")
        response = client.get(
            url,
            {
                "transaction_type": "invoice",
                "status": "unpaid",
                "year": "2024",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert {item["transaction_number"] for item in data} == {"INV-2"}

    def test_invalid_year_ignored(self, client, sample_transactions):
        url = reverse("transaction-list")
        response = client.get(url, {"year": "not-a-year"})

        assert response.status_code == 200
        data = response.json()
        assert len(data) == len(sample_transactions)
