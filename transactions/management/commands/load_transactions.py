import json
import os
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from django.db import transaction as db_transaction

from transactions.models import Transaction
from transactions.serializers import TransactionIngestSerializer

DEFAULT_FIXTURE_PATH = os.path.join(
    "transactions",
    "fixtures",
    "transactions.json",
)


class Command(BaseCommand):
    help = "Load transactions from a JSON file into the database."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--path",
            dest="path",
            default=None,
            help=(
                "Optional path to JSON file. "
                f"Defaults to {DEFAULT_FIXTURE_PATH} inside the project."
            ),
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Parse and validate transactions but do not write to the database.",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete all existing transactions before loading new ones.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        raw_path = options.get("path")
        dry_run: bool = bool(options.get("dry_run"))
        reset: bool = bool(options.get("reset"))

        path = raw_path or os.path.join(settings.BASE_DIR, DEFAULT_FIXTURE_PATH)
        if not os.path.exists(path):
            raise CommandError(f"JSON file not found: {path}")

        self.stdout.write(f"Loading transactions from {path}...")

        data = self._load_json(path)

        objects_to_create: list[Transaction] = []
        total = len(data)
        skipped = 0
        for index, item in enumerate(data, start=1):
            serializer = TransactionIngestSerializer(data=item)
            if not serializer.is_valid():
                skipped += 1
                self.stderr.write(f"Skipping item #{index}: {serializer.errors}")
                continue

            objects_to_create.append(Transaction(**serializer.validated_data))

        if not objects_to_create:
            self.stdout.write("No valid transactions to insert.")
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"Dry run: validated {len(objects_to_create)} transactions "
                    f"(skipped {skipped} of {total}); no changes written."
                )
            )
            return

        with db_transaction.atomic():
            if reset:
                Transaction.objects.all().delete()

            try:
                Transaction.objects.bulk_create(objects_to_create)
            except IntegrityError as exc:
                raise CommandError(
                    "Failed to insert transactions due to duplicate transaction_number "
                    "values already present in the database or within the file. "
                    "Use --reset to start from a clean slate if appropriate."
                ) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"Inserted {len(objects_to_create)} transactions (skipped {skipped} of {total})."
            )
        )

    def _load_json(self, path: str) -> list[dict[str, Any]]:
        """Load and validate the top-level JSON structure.
        Returns a list of dicts, or raises CommandError on invalid structure.
        """
        with open(path) as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as exc:  # pragma: no cover - rare
                raise CommandError(f"Invalid JSON in {path}: {exc}") from exc

        if not isinstance(data, list):
            raise CommandError("Expected top-level JSON array of transactions.")
        return data
