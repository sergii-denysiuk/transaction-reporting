from django.db import models


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        INVOICE = "invoice", "Invoice"
        BILL = "bill", "Bill"
        DIRECT_EXPENSE = "direct_expense", "Direct Expense"

    class Status(models.TextChoices):
        PAID = "paid", "Paid"
        UNPAID = "unpaid", "Unpaid"
        PARTIALLY_PAID = "partially_paid", "Partially Paid"

    transaction_type = models.CharField(
        max_length=32,
        choices=TransactionType.choices,
    )
    status = models.CharField(
        max_length=32,
        choices=Status.choices,
    )

    transaction_number = models.CharField(max_length=64, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    year = models.PositiveSmallIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.transaction_type} {self.transaction_number} ({self.year})"
