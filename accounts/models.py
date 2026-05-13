from __future__ import annotations

from django.conf import settings
from django.db import models


class Profile(models.Model):
    class Role(models.TextChoices):
        RESEARCHER = "researcher", "Registered fan"
        ADMIN = "admin", "Administrator"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        primary_key=True,
    )
    role = models.CharField(
        max_length=16,
        choices=Role.choices,
        default=Role.RESEARCHER,
    )
    favourite_team = models.CharField(max_length=64, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_profile"

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user.username} <{self.role}>"

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN


class DriverFollow(models.Model):
    """Registered users bookmark drivers (no DB FK to `driver` — load order)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="driver_follows",
    )
    driver_id = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "accounts_driver_follow"
        constraints = [
            models.UniqueConstraint(fields=["user", "driver_id"], name="uniq_user_driver_follow"),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.user_id} → driver {self.driver_id}"
