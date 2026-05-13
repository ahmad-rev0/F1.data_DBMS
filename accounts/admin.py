from django.contrib import admin

from .models import DriverFollow, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "favourite_team", "created_at")


@admin.register(DriverFollow)
class DriverFollowAdmin(admin.ModelAdmin):
    list_display = ("user", "driver_id", "created_at")
