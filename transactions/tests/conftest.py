from decimal import Decimal

import pytest

from transactions.models import Transaction


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
        number = explicit_number or f"{transaction_number_prefix}{i}"
        created.append(
            Transaction.objects.create(transaction_number=number, **defaults)
        )
    return created


@pytest.fixture
def transaction_factory(db):
    """Factory for creating one or many transactions.
    Returns a list of created transactions.
    """
    return _factory


@pytest.fixture
def sample_transactions(transaction_factory) -> list[Transaction]:
    """
    Create a small, deterministic dataset:
    - invoice, 2024, paid: 100.00
    - invoice, 2024, unpaid: 75.00
    - bill, 2024, unpaid: 50.00
    """
    return [
        Transaction.objects.create(
            transaction_type=Transaction.TransactionType.INVOICE,
            status=Transaction.Status.PAID,
            transaction_number="INV-PAID-2024-1",
            amount=Decimal("100.00"),
            year=2024,
        ),
        Transaction.objects.create(
            transaction_type=Transaction.TransactionType.INVOICE,
            status=Transaction.Status.UNPAID,
            transaction_number="INV-UNPAID-2024-1",
            amount=Decimal("75.00"),
            year=2024,
        ),
        Transaction.objects.create(
            transaction_type=Transaction.TransactionType.BILL,
            status=Transaction.Status.UNPAID,
            transaction_number="BILL-UNPAID-2024-1",
            amount=Decimal("50.00"),
            year=2024,
        ),
    ]
