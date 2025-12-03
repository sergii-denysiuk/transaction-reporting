import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestTransactionListAPI:
    def test_list_all_transactions(self, client, sample_transactions):
        url = reverse("transaction-list")
        response = client.get(url)

        assert response.status_code == 200
        data = response.json()

        assert set(data.keys()) == {"count", "next", "previous", "results"}
        assert data["count"] == len(sample_transactions)
        assert len(data["results"]) == len(sample_transactions)

    def test_basic_filters(self, client, sample_transactions):
        url = reverse("transaction-list")

        # By transaction_type
        resp = client.get(url, {"transaction_type": "invoice"})
        numbers = {item["transaction_number"] for item in resp.json()["results"]}
        assert numbers == {"INV-PAID-2024-1", "INV-UNPAID-2024-1"}

        # By status
        resp = client.get(url, {"status": "unpaid"})
        numbers = {item["transaction_number"] for item in resp.json()["results"]}
        assert numbers == {"BILL-UNPAID-2024-1", "INV-UNPAID-2024-1"}

        # By year
        resp = client.get(url, {"year": "2024"})
        numbers = {item["transaction_number"] for item in resp.json()["results"]}
        assert numbers == {"BILL-UNPAID-2024-1", "INV-PAID-2024-1", "INV-UNPAID-2024-1"}

        # Combined AND filters
        resp = client.get(
            url,
            {
                "transaction_type": "invoice",
                "status": "unpaid",
                "year": "2024",
            },
        )
        numbers = {item["transaction_number"] for item in resp.json()["results"]}
        assert numbers == {"INV-UNPAID-2024-1"}

    def test_invalid_year_is_ignored(self, client, sample_transactions):
        url = reverse("transaction-list")
        response = client.get(url, {"year": "not-a-year"})

        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == len(sample_transactions)

    def test_pagination_default_page_size(self, client, transaction_factory):
        transaction_factory(count=15)

        url = reverse("transaction-list")
        response = client.get(url)

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 15
        assert len(data["results"]) == 10
        assert data["next"] is not None

    def test_pagination_custom_page_size_and_cap(self, client, transaction_factory):
        transaction_factory(count=150)
        url = reverse("transaction-list")

        # Custom page size smaller than cap
        resp = client.get(url, {"page_size": 5})
        data = resp.json()
        assert data["count"] == 150
        assert len(data["results"]) == 5

        # Very large page size should be capped by settings
        resp = client.get(url, {"page_size": 1000})
        data = resp.json()
        assert data["count"] == 150
        assert len(data["results"]) == 100

    def test_pagination_second_page(self, client, transaction_factory):
        transaction_factory(count=15, transaction_number_prefix="INV-", start_index=0)

        url = reverse("transaction-list")
        response = client.get(url, {"page": 2, "page_size": 10})

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 15
        assert len(data["results"]) == 5
