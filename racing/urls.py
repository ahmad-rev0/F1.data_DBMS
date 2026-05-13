from django.urls import path

from . import views

app_name = "racing"

urlpatterns = [
    path("standings/", views.standings_hub, name="standings_hub"),
    path("circuits/", views.circuit_list, name="circuit_list"),
    path("circuits/<int:circuit_id>/", views.circuit_detail, name="circuit_detail"),
    path("drivers/", views.driver_list, name="driver_list"),
    path("drivers/following/", views.my_drivers, name="my_drivers"),
    path(
        "drivers/<int:driver_id>/export.csv",
        views.driver_results_csv,
        name="driver_export_csv",
    ),
    path("drivers/<int:driver_id>/", views.driver_detail, name="driver_detail"),
    path("constructors/", views.constructor_list, name="constructor_list"),
    path(
        "constructors/<int:constructor_id>/",
        views.constructor_detail,
        name="constructor_detail",
    ),
    path("races/", views.race_list, name="race_list"),
    path("races/<int:race_id>/laps/", views.lap_times_race, name="race_laps"),
    path("races/<int:race_id>/notes/", views.race_notes, name="race_notes"),
    path(
        "races/<int:race_id>/notes/<int:note_id>/delete/",
        views.race_note_delete,
        name="race_note_delete",
    ),
    path(
        "races/<int:race_id>/notes/<int:note_id>/edit/",
        views.race_note_edit,
        name="race_note_edit",
    ),
    path("races/<int:race_id>/", views.race_detail, name="race_detail"),
    path(
        "standings/drivers/<int:year>/",
        views.season_driver_standings,
        name="season_driver_standings",
    ),
    path(
        "standings/constructors/<int:year>/",
        views.season_constructor_standings,
        name="season_constructor_standings",
    ),
    path(
        "sql/procedure-drivers/<int:year>/",
        views.procedure_driver_standings,
        name="procedure_driver_standings",
    ),
    path("search/", views.search, name="search"),
]
