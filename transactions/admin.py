from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_number",
        "amount",
        "year",
        "transaction_type",
        "status",
        "created_at",
        "updated_at",
    )
    list_filter = ("transaction_type", "status", "year")
    search_fields = ("transaction_number",)
    ordering = ("created_at", "updated_at")
