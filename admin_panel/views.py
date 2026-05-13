from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import connection
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from racing.models import Race, RaceResult


def _is_staff(user) -> bool:
    return bool(user.is_authenticated and user.is_staff)


@user_passes_test(_is_staff)
def dashboard(request):
    tables = [
        "season",
        "finishing_status",
        "circuit",
        "driver",
        "constructor",
        "race",
        "race_result",
        "qualifying_session",
        "lap_time",
        "pit_stop",
        "driver_standing",
        "constructor_standing",
        "constructor_race_result",
        "sprint_result",
        "accounts_profile",
        "accounts_driver_follow",
        "racing_race_note",
        "lap_reporting_fact",
    ]
    counts = {}
    try:
        with connection.cursor() as cur:
            for t in tables:
                cur.execute(f"SELECT COUNT(*) FROM `{t}`")
                counts[t] = cur.fetchone()[0]
    except Exception as exc:  # pragma: no cover
        counts = {"error": str(exc)}
    years = []
    try:
        years = sorted(set(Race.objects.values_list("year", flat=True)), reverse=True)[:30]
    except Exception:
        pass
    return render(
        request,
        "admin_panel/dashboard.html",
        {"counts": counts, "standings_years": years},
    )


@user_passes_test(_is_staff)
@require_http_methods(["POST"])
def reload_csv_data(request):
    import subprocess
    import sys
    from pathlib import Path

    from django.conf import settings

    script = Path(settings.BASE_DIR) / "scripts" / "load_f1_csv.py"
    try:
        subprocess.check_call([sys.executable, str(script)], timeout=600)
        messages.success(request, "Championship tables reloaded from CSV files.")
    except Exception as exc:
        messages.error(request, f"Reload failed: {exc}")
    return redirect("admin_panel:dashboard")


@user_passes_test(_is_staff)
@require_http_methods(["GET", "POST"])
def race_results_edit(request, race_id: int):
    race = get_object_or_404(Race.objects.select_related("circuit"), pk=race_id)
    results = list(
        RaceResult.objects.filter(race=race)
        .select_related("driver", "constructor")
        .order_by("position_order")
    )
    if request.method == "POST":
        updated = 0
        for rr in results:
            key = f"pts_{rr.result_id}"
            if key not in request.POST:
                continue
            raw = request.POST[key].strip()
            try:
                new_pts = Decimal(raw)
            except (InvalidOperation, ValueError):
                messages.warning(request, f"Skipped invalid points for result {rr.result_id}.")
                continue
            if new_pts < 0:
                messages.warning(request, f"Skipped negative points for result {rr.result_id}.")
                continue
            if rr.points != new_pts:
                rr.points = new_pts
                rr.save(update_fields=["points"])
                updated += 1
        messages.success(request, f"Updated points on {updated} row(s).")
        return redirect("admin_panel:race_results_edit", race_id=race_id)
    return render(
        request,
        "admin_panel/race_results_edit.html",
        {"race": race, "results": results},
    )