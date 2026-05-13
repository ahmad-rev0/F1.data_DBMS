from django.urls import path

from racing import views_api

urlpatterns = [
    path("health/", views_api.health, name="api_health"),
    path("stats/", views_api.stats, name="api_stats"),
]
