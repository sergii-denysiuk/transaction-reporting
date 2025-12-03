import pytest
from django.urls import reverse

from .models import Transaction


@pytest.fixture
def transaction_factory(db):
    def _factory(
        count: int = 1,
        *,
        transaction_number_prefix: str = "INV-",
        start_index: int = 0,
        **overrides,
    ) -> list[Transaction]:
        defaults = {
            "transaction_type": Transaction.TransactionType.INVOICE,
            "status": Transaction.Status.PAID,
            "amount": "10.00",
            "year": 2024,
        }
        explicit_number = overrides.pop("transaction_number", None)
        defaults.update(overrides)

        created: list[Transaction] = []
        for i in range(start_index, start_index + count):
            tx = Transaction.objects.create(
                transaction_number=explicit_number or f"{transaction_number_prefix}{i}",
                **defaults,
            )
            created.append(tx)
        return created

    return _factory


@pytest.fixture
def sample_transactions(transaction_factory) -> list[Transaction]:
    """Create a small, varied set of transactions for API tests."""
    [tx1] = transaction_factory(
        transaction_number="INV-1",
        transaction_type=Transaction.TransactionType.INVOICE,
        status=Transaction.Status.PAID,
        amount="100.00",
        year=2024,
    )
    [tx2] = transaction_factory(
        transaction_number="BILL-1",
        transaction_type=Transaction.TransactionType.BILL,
        status=Transaction.Status.UNPAID,
        amount="50.00",
        year=2023,
    )
    [tx3] = transaction_factory(
        transaction_number="INV-2",
        transaction_type=Transaction.TransactionType.INVOICE,
        status=Transaction.Status.UNPAID,
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

        # Paginated response shape
        assert set(data.keys()) == {"count", "next", "previous", "results"}
        assert data["count"] == len(sample_transactions)
        assert len(data["results"]) == len(sample_transactions)

        # Ensure expected keys are present on an item
        item = data["results"][0]
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
        results = data["results"]
        assert {item["transaction_number"] for item in results} == {"INV-1", "INV-2"}

    def test_filter_by_status(self, client, sample_transactions):
        url = reverse("transaction-list")
        response = client.get(url, {"status": "unpaid"})

        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        assert {item["transaction_number"] for item in results} == {"BILL-1", "INV-2"}

    def test_filter_by_year(self, client, sample_transactions):
        url = reverse("transaction-list")
        response = client.get(url, {"year": "2023"})

        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        assert {item["transaction_number"] for item in results} == {"BILL-1"}

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
        results = data["results"]
        assert {item["transaction_number"] for item in results} == {"INV-2"}

    def test_invalid_year_ignored(self, client, sample_transactions):
        url = reverse("transaction-list")
        response = client.get(url, {"year": "not-a-year"})

        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        assert len(results) == len(sample_transactions)

    def test_pagination_default_page_size(self, client, transaction_factory):
        """Default page_size should limit results on first page."""
        transaction_factory(count=15)

        url = reverse("transaction-list")
        response = client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 15
        assert len(data["results"]) == 10
        assert data["next"] is not None

    def test_pagination_custom_page_size(self, client, transaction_factory):
        transaction_factory(count=7)

        url = reverse("transaction-list")
        response = client.get(url, {"page_size": 5})

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 7
        assert len(data["results"]) == 5

    def test_pagination_second_page(self, client, transaction_factory):
        # Use zero-padded numbers to make ordering deterministic
        transaction_factory(
            count=15,
            transaction_number_prefix="INV-",
            start_index=0,
        )

        url = reverse("transaction-list")
        response = client.get(url, {"page": 2, "page_size": 10})

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 15
        assert len(data["results"]) == 5

        numbers = [item["transaction_number"] for item in data["results"]]
        assert numbers == sorted(numbers)

    def test_pagination_page_size_capped(self, client, transaction_factory):
        transaction_factory(count=150)

        url = reverse("transaction-list")
        response = client.get(url, {"page_size": 1000})

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 150
        assert len(data["results"]) == 100
