"""Public landing pages."""
from __future__ import annotations

from django.db import connection
from django.shortcuts import render

_STATS_SQL = """
SELECT
  (SELECT COUNT(*) FROM driver) AS driver_count,
  (SELECT COUNT(*) FROM race) AS race_count,
  (SELECT COUNT(*) FROM circuit) AS circuit_count,
  (SELECT COUNT(*) FROM lap_time) AS lap_time_count,
  (SELECT COUNT(*) FROM race_result) AS race_result_count
"""


def home(request):
    stats = {
        "driver_count": 0,
        "race_count": 0,
        "circuit_count": 0,
        "lap_time_count": 0,
        "lap_reporting_fact_count": None,
        "race_result_count": 0,
    }
    try:
        with connection.cursor() as cur:
            cur.execute(_STATS_SQL)
            row = cur.fetchone()
            if row:
                keys = (
                    "driver_count",
                    "race_count",
                    "circuit_count",
                    "lap_time_count",
                    "race_result_count",
                )
                stats.update(dict(zip(keys, row)))
        try:
            with connection.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM lap_reporting_fact")
                stats["lap_reporting_fact_count"] = cur.fetchone()[0]
        except Exception:
            stats["lap_reporting_fact_count"] = None
    except Exception:
        pass
    return render(request, "core/home.html", {"stats": stats})


def about(request):
    return render(request, "core/about.html")
