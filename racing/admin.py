from django.contrib import admin

from .models import RaceNote


@admin.register(RaceNote)
class RaceNoteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "race_id", "updated_at")
    list_filter = ("race_id",)
    search_fields = ("body",)
