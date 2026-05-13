"""Quick insert / search / delete timing against MySQL (course performance evidence).

Run from repo root:
    .venv\\Scripts\\python scripts\\benchmark_performance.py
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pymysql
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from f1_platform.mysql_tls import pymysql_ssl_kwargs


def connect():
    load_dotenv(ROOT / ".env")
    return pymysql.connect(
        host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=os.environ.get("MYSQL_USER", "f1_app"),
        password=os.environ.get("MYSQL_PASSWORD", ""),
        database=os.environ.get("MYSQL_DATABASE", "formula1"),
        charset="utf8mb4",
        **pymysql_ssl_kwargs(),
    )


def main() -> None:
    conn = connect()
    try:
        cur = conn.cursor()

        t0 = time.perf_counter()
        cur.execute(
            "INSERT INTO season (year, url) VALUES (2099, 'https://benchmark.local') "
            "ON DUPLICATE KEY UPDATE url = VALUES(url)"
        )
        conn.commit()
        t_insert = time.perf_counter() - t0
        print(f"insert_season_placeholder_s: {t_insert:.4f}")

        t0 = time.perf_counter()
        cur.execute(
            "SELECT rr.result_id, d.surname FROM race_result rr "
            "JOIN driver d ON d.driver_id = rr.driver_id "
            "WHERE rr.race_id = (SELECT MAX(race_id) FROM race) "
            "ORDER BY rr.position_order LIMIT 500"
        )
        cur.fetchall()
        t_search = time.perf_counter() - t0
        print(f"search_join_500_rows_s: {t_search:.4f}")

        t0 = time.perf_counter()
        cur.execute("DELETE FROM season WHERE year = 2099")
        conn.commit()
        t_delete = time.perf_counter() - t0
        print(f"delete_season_placeholder_s: {t_delete:.4f}")

        cur.execute(
            "SELECT COUNT(*) FROM lap_time WHERE race_id = (SELECT MAX(race_id) FROM race)"
        )
        n = cur.fetchone()[0]
        print(f"lap_rows_last_race: {n}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
