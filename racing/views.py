"""Browse circuits, drivers, constructors, races, standings, exports, and notes."""
from __future__ import annotations

import csv
from io import StringIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Max, Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.models import DriverFollow

from .forms import RaceNoteForm
from .models import (
    Circuit,
    Constructor,
    ConstructorStanding,
    Driver,
    DriverStanding,
    LapTime,
    QualifyingSession,
    Race,
    RaceNote,
    RaceResult,
)


def circuit_list(request: HttpRequest) -> HttpResponse:
    qs = Circuit.objects.all().order_by("country", "name")
    paginator = Paginator(qs, 30)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "racing/circuit_list.html", {"page": page})


def circuit_detail(request: HttpRequest, circuit_id: int) -> HttpResponse:
    circuit = get_object_or_404(Circuit, pk=circuit_id)
    races = (
        Race.objects.filter(circuit=circuit)
        .select_related("circuit")
        .order_by("-year", "-round_num")[:40]
    )
    return render(
        request,
        "racing/circuit_detail.html",
        {"circuit": circuit, "races": races},
    )


def driver_list(request: HttpRequest) -> HttpResponse:
    qs = Driver.objects.all().order_by("surname", "forename")
    q = (request.GET.get("q") or "").strip()
    if q:
        qs = qs.filter(
            Q(surname__icontains=q)
            | Q(forename__icontains=q)
            | Q(driver_ref__icontains=q)
        )
    paginator = Paginator(qs, 40)
    page = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "racing/driver_list.html",
        {"page": page, "q": q},
    )


@require_http_methods(["GET", "POST"])
def driver_detail(request: HttpRequest, driver_id: int) -> HttpResponse:
    driver = get_object_or_404(Driver, pk=driver_id)
    results = (
        RaceResult.objects.filter(driver=driver)
        .select_related("race", "constructor", "finishing_status")
        .order_by("-race__race_date")[:30]
    )
    following = False
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        following = DriverFollow.objects.filter(
            user=request.user,
            driver_id=driver_id,
        ).exists()
        if following:
            DriverFollow.objects.filter(
                user=request.user,
                driver_id=driver_id,
            ).delete()
        else:
            DriverFollow.objects.create(
                user=request.user,
                driver_id=driver_id,
            )
        return redirect("racing:driver_detail", driver_id=driver_id)
    if request.user.is_authenticated:
        following = DriverFollow.objects.filter(
            user=request.user,
            driver_id=driver_id,
        ).exists()
    return render(
        request,
        "racing/driver_detail.html",
        {
            "driver": driver,
            "results": results,
            "following": following,
        },
    )


def constructor_list(request: HttpRequest) -> HttpResponse:
    qs = Constructor.objects.all().order_by("name")
    paginator = Paginator(qs, 30)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "racing/constructor_list.html", {"page": page})


def constructor_detail(request: HttpRequest, constructor_id: int) -> HttpResponse:
    constructor = get_object_or_404(Constructor, pk=constructor_id)
    recent = (
        RaceResult.objects.filter(constructor=constructor)
        .select_related("race", "driver")
        .order_by("-race__race_date")[:35]
    )
    return render(
        request,
        "racing/constructor_detail.html",
        {"constructor": constructor, "recent": recent},
    )


def race_list(request: HttpRequest) -> HttpResponse:
    qs = Race.objects.select_related("circuit").order_by("-year", "-round_num")
    year_str = (request.GET.get("year") or "").strip()
    selected_year: int | None = None
    if year_str.isdigit():
        selected_year = int(year_str)
        qs = qs.filter(year=selected_year)
    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get("page"))
    years = sorted(set(Race.objects.values_list("year", flat=True)), reverse=True)[:40]
    return render(
        request,
        "racing/race_list.html",
        {
            "page": page,
            "years": years,
            "selected_year": selected_year,
        },
    )


def race_detail(request: HttpRequest, race_id: int) -> HttpResponse:
    race = get_object_or_404(Race.objects.select_related("circuit"), pk=race_id)
    results = (
        RaceResult.objects.filter(race=race)
        .select_related("driver", "constructor", "finishing_status")
        .order_by("position_order")
    )
    qualifying = (
        QualifyingSession.objects.filter(race=race)
        .select_related("driver", "constructor")
        .order_by("qualify_position")
    )
    note_count = 0
    if request.user.is_authenticated:
        note_count = RaceNote.objects.filter(user=request.user, race_id=race_id).count()
    return render(
        request,
        "racing/race_detail.html",
        {
            "race": race,
            "results": results,
            "qualifying": qualifying,
            "note_count": note_count,
        },
    )


def search(request: HttpRequest) -> HttpResponse:
    q = (request.GET.get("q") or "").strip()
    drivers = []
    if q:
        drivers = list(
            Driver.objects.filter(
                Q(surname__icontains=q)
                | Q(forename__icontains=q)
                | Q(code__iexact=q)
            ).order_by("surname")[:50]
        )
    return render(request, "racing/search.html", {"q": q, "drivers": drivers})


@login_required
def my_drivers(request: HttpRequest) -> HttpResponse:
    follows = DriverFollow.objects.filter(user=request.user).order_by("-created_at")
    driver_ids = [f.driver_id for f in follows]
    drivers = {d.driver_id: d for d in Driver.objects.filter(driver_id__in=driver_ids)}
    rows = [(drivers.get(f.driver_id), f) for f in follows if drivers.get(f.driver_id)]
    return render(request, "racing/my_drivers.html", {"rows": rows})


def standings_hub(request: HttpRequest) -> HttpResponse:
    years = sorted(set(Race.objects.values_list("year", flat=True)), reverse=True)[:35]
    latest = years[0] if years else None
    return render(
        request,
        "racing/standings_hub.html",
        {"years": years, "latest": latest},
    )


def season_driver_standings(request: HttpRequest, year: int) -> HttpResponse:
    last_race_id = Race.objects.filter(year=year).aggregate(m=Max("race_id"))["m"]
    if last_race_id is None:
        return render(
            request,
            "racing/standings_drivers.html",
            {"year": year, "rows": [], "last_race": None},
        )
    last_race = Race.objects.select_related("circuit").get(pk=last_race_id)
    rows = (
        DriverStanding.objects.filter(race_id=last_race_id)
        .select_related("driver")
        .order_by("championship_position", "driver__surname")
    )
    return render(
        request,
        "racing/standings_drivers.html",
        {"year": year, "rows": rows, "last_race": last_race},
    )


def season_constructor_standings(request: HttpRequest, year: int) -> HttpResponse:
    last_race_id = Race.objects.filter(year=year).aggregate(m=Max("race_id"))["m"]
    if last_race_id is None:
        return render(
            request,
            "racing/standings_constructors.html",
            {"year": year, "rows": [], "last_race": None},
        )
    last_race = Race.objects.select_related("circuit").get(pk=last_race_id)
    rows = (
        ConstructorStanding.objects.filter(race_id=last_race_id)
        .select_related("constructor")
        .order_by("championship_position", "constructor__name")
    )
    return render(
        request,
        "racing/standings_constructors.html",
        {"year": year, "rows": rows, "last_race": last_race},
    )


def procedure_driver_standings(request: HttpRequest, year: int) -> HttpResponse:
    """Render rows from stored procedure `sp_driver_standings_end_of_year`."""
    rows: list[tuple] = []
    err = ""
    try:
        with connection.cursor() as cur:
            cur.execute("CALL sp_driver_standings_end_of_year(%s)", [year])
            rows = cur.fetchall()
            if cur.nextset():
                pass
    except Exception as exc:  # pragma: no cover - missing procedure on fresh DB
        err = str(exc)
    return render(
        request,
        "racing/procedure_standings.html",
        {"year": year, "rows": rows, "error": err},
    )


def lap_times_race(request: HttpRequest, race_id: int) -> HttpResponse:
    race = get_object_or_404(Race.objects.select_related("circuit"), pk=race_id)
    qs = LapTime.objects.filter(race_id=race_id).order_by("lap_num", "driver_id")
    paginator = Paginator(qs, 200)
    page = paginator.get_page(request.GET.get("page"))
    driver_ids = {row.driver_id for row in page.object_list}
    drivers = {d.driver_id: d for d in Driver.objects.filter(driver_id__in=driver_ids)}
    rows = [(lt, drivers.get(lt.driver_id)) for lt in page.object_list]
    return render(
        request,
        "racing/lap_times.html",
        {"race": race, "page": page, "rows": rows},
    )


def driver_results_csv(request: HttpRequest, driver_id: int) -> HttpResponse:
    driver = get_object_or_404(Driver, pk=driver_id)
    rows = (
        RaceResult.objects.filter(driver=driver)
        .select_related("race", "constructor", "finishing_status")
        .order_by("-race__race_date")
    )
    buf = StringIO()
    w = csv.writer(buf)
    w.writerow(
        [
            "race_date",
            "grand_prix",
            "circuit",
            "constructor",
            "grid",
            "finish",
            "points",
            "status",
        ]
    )
    for rr in rows:
        w.writerow(
            [
                rr.race.race_date.isoformat(),
                rr.race.name,
                rr.race.circuit.name,
                rr.constructor.name,
                rr.grid_pos,
                rr.finish_position if rr.finish_position is not None else rr.position_text,
                str(rr.points),
                rr.finishing_status.label,
            ]
        )
    resp = HttpResponse(buf.getvalue(), content_type="text/csv; charset=utf-8")
    safe = f"{driver.surname}_{driver.forename}".replace(" ", "_")
    resp["Content-Disposition"] = f'attachment; filename="driver_{driver_id}_{safe}.csv"'
    return resp


@login_required
@require_http_methods(["GET", "POST"])
def race_notes(request: HttpRequest, race_id: int) -> HttpResponse:
    race = get_object_or_404(Race, pk=race_id)
    notes = RaceNote.objects.filter(user=request.user, race_id=race_id)
    if request.method == "POST":
        form = RaceNoteForm(request.POST)
        if form.is_valid():
            n = form.save(commit=False)
            n.user = request.user
            n.race_id = race_id
            n.save()
            messages.success(request, "Note saved.")
            return redirect("racing:race_notes", race_id=race_id)
    else:
        form = RaceNoteForm()
    return render(
        request,
        "racing/race_notes.html",
        {"race": race, "notes": notes, "form": form},
    )


@login_required
@require_http_methods(["POST"])
def race_note_delete(request: HttpRequest, race_id: int, note_id: int) -> HttpResponse:
    get_object_or_404(Race, pk=race_id)
    note = get_object_or_404(RaceNote, pk=note_id, user=request.user, race_id=race_id)
    note.delete()
    messages.info(request, "Note deleted.")
    return redirect("racing:race_notes", race_id=race_id)


@login_required
@require_http_methods(["GET", "POST"])
def race_note_edit(request: HttpRequest, race_id: int, note_id: int) -> HttpResponse:
    race = get_object_or_404(Race, pk=race_id)
    note = get_object_or_404(RaceNote, pk=note_id, user=request.user, race_id=race_id)
    if request.method == "POST":
        form = RaceNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "Note updated.")
            return redirect("racing:race_notes", race_id=race_id)
    else:
        form = RaceNoteForm(instance=note)
    return render(
        request,
        "racing/race_note_edit.html",
        {"race": race, "note": note, "form": form},
    )