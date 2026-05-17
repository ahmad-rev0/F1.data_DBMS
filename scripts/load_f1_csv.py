"""Bulk-load Kaggle Formula 1 CSV files into MySQL (snake_case schema).

Usage (from repo root, with venv active):
    python scripts/load_f1_csv.py

Requires: pandas, pymysql, python-dotenv; MySQL schema already applied
(`database/schema.sql`). Connection parameters are read from `.env`.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import pymysql
from dotenv import load_dotenv
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CSV_DIR = PROJECT_ROOT / "CSV files"
_NA = [r"\N", "\\N"]


def _read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(CSV_DIR / name, na_values=_NA, keep_default_na=True, low_memory=False)


def _connect() -> pymysql.connections.Connection:
    load_dotenv(PROJECT_ROOT / ".env")
    return pymysql.connect(
        host=os.environ.get("MYSQL_HOST", "127.0.0.1"),
        port=int(os.environ.get("MYSQL_PORT", "3306")),
        user=os.environ.get("MYSQL_USER", "f1_app"),
        password=os.environ.get("MYSQL_PASSWORD", ""),
        database=os.environ.get("MYSQL_DATABASE", "formula1"),
        charset="utf8mb4",
        autocommit=False,
    )


def _rows(df: pd.DataFrame, columns: list[str]) -> list[tuple]:
    out: list[tuple] = []
    for row in df[columns].itertuples(index=False, name=None):
        out.append(tuple(None if pd.isna(x) else x for x in row))
    return out


def _executemany(
    cur: pymysql.cursors.Cursor,
    table: str,
    columns: list[str],
    rows: list[tuple],
    chunk: int = 8000,
) -> None:
    if not rows:
        return
    col_sql = ", ".join(f"`{c}`" for c in columns)
    ph = ", ".join(["%s"] * len(columns))
    sql = f"INSERT INTO `{table}` ({col_sql}) VALUES ({ph})"
    for i in tqdm(range(0, len(rows), chunk), desc=f"{table}"):
        cur.executemany(sql, rows[i : i + chunk])


def load_all() -> None:
    if not CSV_DIR.is_dir():
        raise SystemExit(f"CSV folder not found: {CSV_DIR}")

    conn = _connect()
    try:
        cur = conn.cursor()
        cur.execute("SET FOREIGN_KEY_CHECKS = 0")
        for tbl in (
            "sprint_result",
            "constructor_race_result",
            "constructor_standing",
            "driver_standing",
            "pit_stop",
            "lap_reporting_fact",
            "lap_time",
            "qualifying_session",
            "race_result",
            "race",
            "constructor",
            "driver",
            "circuit",
            "finishing_status",
            "season",
        ):
            cur.execute(f"TRUNCATE TABLE `{tbl}`")
        cur.execute("SET FOREIGN_KEY_CHECKS = 1")
        conn.commit()

        # --- reference ---
        s = _read_csv("seasons.csv")
        _executemany(cur, "season", ["year", "url"], _rows(s, ["year", "url"]))

        st = _read_csv("status.csv")
        st = st.rename(columns={"statusId": "status_id", "status": "label"})
        _executemany(
            cur,
            "finishing_status",
            ["status_id", "label"],
            _rows(st, ["status_id", "label"]),
        )

        c = _read_csv("circuits.csv")
        c = c.rename(
            columns={
                "circuitId": "circuit_id",
                "circuitRef": "circuit_ref",
                "lat": "lat",
                "lng": "lng",
                "alt": "alt",
            }
        )
        _executemany(
            cur,
            "circuit",
            [
                "circuit_id",
                "circuit_ref",
                "name",
                "location",
                "country",
                "lat",
                "lng",
                "alt",
                "url",
            ],
            _rows(
                c,
                [
                    "circuit_id",
                    "circuit_ref",
                    "name",
                    "location",
                    "country",
                    "lat",
                    "lng",
                    "alt",
                    "url",
                ],
            ),
        )

        d = _read_csv("drivers.csv")
        d = d.rename(
            columns={
                "driverId": "driver_id",
                "driverRef": "driver_ref",
                "number": "driver_number",
            }
        )
        _executemany(
            cur,
            "driver",
            [
                "driver_id",
                "driver_ref",
                "driver_number",
                "code",
                "forename",
                "surname",
                "dob",
                "nationality",
                "url",
            ],
            _rows(
                d,
                [
                    "driver_id",
                    "driver_ref",
                    "driver_number",
                    "code",
                    "forename",
                    "surname",
                    "dob",
                    "nationality",
                    "url",
                ],
            ),
        )

        cons = _read_csv("constructors.csv")
        cons = cons.rename(
            columns={
                "constructorId": "constructor_id",
                "constructorRef": "constructor_ref",
            }
        )
        _executemany(
            cur,
            "constructor",
            ["constructor_id", "constructor_ref", "name", "nationality", "url"],
            _rows(
                cons,
                ["constructor_id", "constructor_ref", "name", "nationality", "url"],
            ),
        )

        r = _read_csv("races.csv")
        r = r.rename(
            columns={
                "raceId": "race_id",
                "circuitId": "circuit_id",
                "round": "round_num",
                "date": "race_date",
                "time": "race_time",
            }
        )
        _executemany(
            cur,
            "race",
            [
                "race_id",
                "year",
                "round_num",
                "circuit_id",
                "name",
                "race_date",
                "race_time",
                "url",
                "fp1_date",
                "fp1_time",
                "fp2_date",
                "fp2_time",
                "fp3_date",
                "fp3_time",
                "quali_date",
                "quali_time",
                "sprint_date",
                "sprint_time",
            ],
            _rows(
                r,
                [
                    "race_id",
                    "year",
                    "round_num",
                    "circuit_id",
                    "name",
                    "race_date",
                    "race_time",
                    "url",
                    "fp1_date",
                    "fp1_time",
                    "fp2_date",
                    "fp2_time",
                    "fp3_date",
                    "fp3_time",
                    "quali_date",
                    "quali_time",
                    "sprint_date",
                    "sprint_time",
                ],
            ),
        )

        rr = _read_csv("results.csv")
        rr = rr.rename(
            columns={
                "resultId": "result_id",
                "raceId": "race_id",
                "driverId": "driver_id",
                "constructorId": "constructor_id",
                "number": "car_number",
                "grid": "grid_pos",
                "position": "finish_position",
                "positionText": "position_text",
                "positionOrder": "position_order",
                "time": "finish_time",
                "rank": "fastest_lap_rank",
                "fastestLap": "fastest_lap",
                "fastestLapTime": "fastest_lap_time",
                "fastestLapSpeed": "fastest_lap_speed",
                "statusId": "status_id",
            }
        )
        _executemany(
            cur,
            "race_result",
            [
                "result_id",
                "race_id",
                "driver_id",
                "constructor_id",
                "car_number",
                "grid_pos",
                "finish_position",
                "position_text",
                "position_order",
                "points",
                "laps",
                "finish_time",
                "milliseconds",
                "fastest_lap",
                "fastest_lap_rank",
                "fastest_lap_time",
                "fastest_lap_speed",
                "status_id",
            ],
            _rows(
                rr,
                [
                    "result_id",
                    "race_id",
                    "driver_id",
                    "constructor_id",
                    "car_number",
                    "grid_pos",
                    "finish_position",
                    "position_text",
                    "position_order",
                    "points",
                    "laps",
                    "finish_time",
                    "milliseconds",
                    "fastest_lap",
                    "fastest_lap_rank",
                    "fastest_lap_time",
                    "fastest_lap_speed",
                    "status_id",
                ],
            ),
        )

        q = _read_csv("qualifying.csv")
        q = q.rename(
            columns={
                "qualifyId": "qualify_id",
                "raceId": "race_id",
                "driverId": "driver_id",
                "constructorId": "constructor_id",
                "number": "car_number",
                "position": "qualify_position",
            }
        )
        _executemany(
            cur,
            "qualifying_session",
            [
                "qualify_id",
                "race_id",
                "driver_id",
                "constructor_id",
                "car_number",
                "qualify_position",
                "q1",
                "q2",
                "q3",
            ],
            _rows(
                q,
                [
                    "qualify_id",
                    "race_id",
                    "driver_id",
                    "constructor_id",
                    "car_number",
                    "qualify_position",
                    "q1",
                    "q2",
                    "q3",
                ],
            ),
        )

        lt = _read_csv("lap_times.csv")
        lt = lt.rename(
            columns={
                "raceId": "race_id",
                "driverId": "driver_id",
                "lap": "lap_num",
                "position": "lap_position",
                "time": "lap_time",
            }
        )
        _executemany(
            cur,
            "lap_time",
            [
                "race_id",
                "driver_id",
                "lap_num",
                "lap_position",
                "lap_time",
                "milliseconds",
            ],
            _rows(
                lt,
                [
                    "race_id",
                    "driver_id",
                    "lap_num",
                    "lap_position",
                    "lap_time",
                    "milliseconds",
                ],
            ),
        )

        print("Materializing lap_reporting_fact (denormalized copy of lap_time) ...")
        cur.execute("DELETE FROM lap_reporting_fact")
        cur.execute(
            """
            INSERT INTO lap_reporting_fact (
                race_id, driver_id, lap_num, lap_position, lap_time, milliseconds,
                season_year, grand_prix, circuit_country, driver_code, driver_surname
            )
            SELECT
                lt.race_id,
                lt.driver_id,
                lt.lap_num,
                lt.lap_position,
                lt.lap_time,
                lt.milliseconds,
                r.year,
                r.name,
                c.country,
                d.code,
                d.surname
            FROM lap_time lt
            INNER JOIN race r ON r.race_id = lt.race_id
            INNER JOIN circuit c ON c.circuit_id = r.circuit_id
            INNER JOIN driver d ON d.driver_id = lt.driver_id
            """
        )

        ps = _read_csv("pit_stops.csv")
        ps = ps.rename(
            columns={
                "raceId": "race_id",
                "driverId": "driver_id",
                "stop": "stop_num",
                "lap": "lap_num",
                "time": "clock_time",
            }
        )
        _executemany(
            cur,
            "pit_stop",
            [
                "race_id",
                "driver_id",
                "stop_num",
                "lap_num",
                "clock_time",
                "duration",
                "milliseconds",
            ],
            _rows(
                ps,
                [
                    "race_id",
                    "driver_id",
                    "stop_num",
                    "lap_num",
                    "clock_time",
                    "duration",
                    "milliseconds",
                ],
            ),
        )

        ds = _read_csv("driver_standings.csv")
        ds = ds.rename(
            columns={
                "driverStandingsId": "driver_standing_id",
                "raceId": "race_id",
                "driverId": "driver_id",
                "position": "championship_position",
                "positionText": "position_text",
            }
        )
        _executemany(
            cur,
            "driver_standing",
            [
                "driver_standing_id",
                "race_id",
                "driver_id",
                "points",
                "championship_position",
                "position_text",
                "wins",
            ],
            _rows(
                ds,
                [
                    "driver_standing_id",
                    "race_id",
                    "driver_id",
                    "points",
                    "championship_position",
                    "position_text",
                    "wins",
                ],
            ),
        )

        cs = _read_csv("constructor_standings.csv")
        cs = cs.rename(
            columns={
                "constructorStandingsId": "constructor_standing_id",
                "raceId": "race_id",
                "constructorId": "constructor_id",
                "position": "championship_position",
                "positionText": "position_text",
            }
        )
        _executemany(
            cur,
            "constructor_standing",
            [
                "constructor_standing_id",
                "race_id",
                "constructor_id",
                "points",
                "championship_position",
                "position_text",
                "wins",
            ],
            _rows(
                cs,
                [
                    "constructor_standing_id",
                    "race_id",
                    "constructor_id",
                    "points",
                    "championship_position",
                    "position_text",
                    "wins",
                ],
            ),
        )

        cr = _read_csv("constructor_results.csv")
        cr = cr.rename(
            columns={
                "constructorResultsId": "constructor_result_id",
                "raceId": "race_id",
                "constructorId": "constructor_id",
                "status": "result_status",
            }
        )
        _executemany(
            cur,
            "constructor_race_result",
            [
                "constructor_result_id",
                "race_id",
                "constructor_id",
                "points",
                "result_status",
            ],
            _rows(
                cr,
                [
                    "constructor_result_id",
                    "race_id",
                    "constructor_id",
                    "points",
                    "result_status",
                ],
            ),
        )

        sp = _read_csv("sprint_results.csv")
        sp = sp.rename(
            columns={
                "resultId": "sprint_result_id",
                "raceId": "race_id",
                "driverId": "driver_id",
                "constructorId": "constructor_id",
                "number": "car_number",
                "grid": "grid_pos",
                "position": "finish_position",
                "positionText": "position_text",
                "positionOrder": "position_order",
                "time": "finish_time",
                "fastestLap": "fastest_lap",
                "fastestLapTime": "fastest_lap_time",
                "statusId": "status_id",
            }
        )
        _executemany(
            cur,
            "sprint_result",
            [
                "sprint_result_id",
                "race_id",
                "driver_id",
                "constructor_id",
                "car_number",
                "grid_pos",
                "finish_position",
                "position_text",
                "position_order",
                "points",
                "laps",
                "finish_time",
                "milliseconds",
                "fastest_lap",
                "fastest_lap_time",
                "status_id",
            ],
            _rows(
                sp,
                [
                    "sprint_result_id",
                    "race_id",
                    "driver_id",
                    "constructor_id",
                    "car_number",
                    "grid_pos",
                    "finish_position",
                    "position_text",
                    "position_order",
                    "points",
                    "laps",
                    "finish_time",
                    "milliseconds",
                    "fastest_lap",
                    "fastest_lap_time",
                    "status_id",
                ],
            ),
        )

        conn.commit()
        print("Load complete.")
    finally:
        conn.close()


if __name__ == "__main__":
    try:
        load_all()
    except Exception as exc:  # pragma: no cover - CLI helper
        print(exc, file=sys.stderr)
        sys.exit(1)
