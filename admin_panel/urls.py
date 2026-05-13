from django.urls import path

from . import views

app_name = "admin_panel"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("reload-csv/", views.reload_csv_data, name="reload_csv"),
    path(
        "race-results/<int:race_id>/",
        views.race_results_edit,
        name="race_results_edit",
    ),
]
