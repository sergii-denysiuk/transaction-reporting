from django.urls import path

from .views import TransactionListView, TransactionReportView

urlpatterns = [
    path("transactions/", TransactionListView.as_view(), name="transaction-list"),
    path(
        "transactions/report/",
        TransactionReportView.as_view(),
        name="transaction-report",
    ),
]
