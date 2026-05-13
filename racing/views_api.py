"""Read-only JSON endpoints for external frontends (e.g. Vercel)."""
from __future__ import annotations

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from racing.models import Circuit, Constructor, Driver, LapReportingFact, LapTime, Race


@require_GET
def health(request):
    return JsonResponse({"status": "ok"})


@require_GET
def stats(request):
    data = {
        "circuits": Circuit.objects.count(),
        "constructors": Constructor.objects.count(),
        "drivers": Driver.objects.count(),
        "races": Race.objects.count(),
        "lap_times": LapTime.objects.count(),
        "lap_reporting_fact": LapReportingFact.objects.count(),
    }
    return JsonResponse(data)
