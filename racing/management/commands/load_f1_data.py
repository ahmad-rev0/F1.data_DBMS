"""Reload championship tables from `CSV files/` (same logic as `scripts/load_f1_csv.py`)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Truncate F1 tables and bulk-load CSVs (requires MySQL + schema already applied)."

    def handle(self, *args, **options) -> None:
        script = Path(settings.BASE_DIR) / "scripts" / "load_f1_csv.py"
        self.stdout.write(f"Running {script} …")
        subprocess.check_call([sys.executable, str(script)])
        self.stdout.write(self.style.SUCCESS("Load finished."))
