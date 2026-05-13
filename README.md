# Formula 1 DBMS project (Django + MySQL)

Course scaffold for **COMP3013**: hand-written MySQL schema (`database/schema.sql`), bulk CSV load (`scripts/load_f1_csv.py`), and a Django front-end that maps championship tables as **unmanaged** models while Django owns authentication plus `accounts_profile` / `accounts_driver_follow`.

## Prerequisites

- Python 3.11+ (project venv under `.venv/`)
- Docker Desktop (recommended) **or** a local MySQL 8 server
- CSV bundle in `CSV files/` (Kaggle: *Formula 1 World Championship (1950–2020)*, Rohan Rao)

## Quick start

1. **Environment**

   ```powershell
   cd "d:\BNBU courses\DBMS COMP3013\dbms_project_Formula1"
   copy .env.example .env
   # edit .env if passwords differ
   ```

2. **MySQL**

   **Option A — Docker (if installed):**

   ```powershell
   docker compose up -d mysql
   ```

   Then apply `database/schema.sql` and `database/indexes.sql` to the `formula1` database (see Docker docs for piping SQL on your OS).

   **Option B — Windows service `MySQL80` (common on lab PCs):**

   1. Put your **real MySQL root password** in `.env` as `MYSQL_ROOT_PASSWORD=...` (the value from MySQL Installer, *not* the placeholder in `.env.example` unless you actually set root to that).
   2. From the repo root, run the automated script (creates DB/user, applies DDL, `migrate`, loads CSVs):

      ```powershell
      .\scripts\setup_local_mysql.ps1
      ```

      Or pass the password once without storing it in `.env`:

      ```powershell
      .\run_all.ps1 -RootPassword 'YourMySQLRootPassword'
      ```

      `run_all.ps1` runs the same setup, then starts `runserver`.

3. **Python venv** (do this before the MySQL setup script)

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\pip install -r requirements.txt
   ```

4. **Django + data load**

   - If you used **Option B** (`setup_local_mysql.ps1` or `run_all.ps1`), **steps 4–5 here are already done** inside the script.
   - If you used **Docker** or applied SQL manually, run:

   ```powershell
   .\.venv\Scripts\python manage.py migrate
   .\.venv\Scripts\python scripts\load_f1_csv.py
   ```

5. **Run the site**

   ```powershell
   .\.venv\Scripts\python manage.py createsuperuser
   .\.venv\Scripts\python manage.py runserver
   ```

   (If you used `run_all.ps1`, the server is already starting after setup; press Ctrl+C to stop, then use `runserver` again whenever you want.)

   - Public browse: `/`, `/circuits/`, `/drivers/`, `/races/`, …
   - Staff dashboard: `/admin-panel/` (requires `is_staff` on the user)
   - Django admin: `/django-admin/`

## Layout

| Path | Role |
| --- | --- |
| `database/schema.sql` | Reference tables + FK graph |
| `database/indexes.sql` | Extra performance indexes |
| `scripts/load_f1_csv.py` | Truncate + bulk insert from `CSV files/` |
| `racing/models.py` | Unmanaged ORM ↔ MySQL |
| `accounts/` | Registration, profiles, driver follows (insert/delete) |
| `templates/` | Bootstrap 5 UI |

## Next steps for the rubric

Add stored procedures, triggers, benchmark scripts, richer admin CRUD on `race_result`, CSV/PDF exports, and ER/report figures — the plumbing above is the baseline.
