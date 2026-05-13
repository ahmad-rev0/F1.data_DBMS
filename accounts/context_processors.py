from __future__ import annotations

from django.http import HttpRequest


def user_role(request: HttpRequest) -> dict:
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {"is_admin_role": False, "is_fan_role": False}
    profile = getattr(user, "profile", None)
    return {
        "is_admin_role": bool(user.is_staff or (profile and profile.role == "admin")),
        "is_fan_role": bool(profile and profile.role == "researcher"),
    }
