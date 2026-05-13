"""Unmanaged ORM models mapped to `database/schema.sql`, plus managed app tables."""
from __future__ import annotations

from django.conf import settings
from django.db import models


class Season(models.Model):
    year = models.SmallIntegerField(primary_key=True)
    url = models.CharField(max_length=512)

    class Meta:
        managed = False
        db_table = "season"


class FinishingStatus(models.Model):
    status_id = models.SmallIntegerField(primary_key=True)
    label = models.CharField(max_length=128)

    class Meta:
        managed = False
        db_table = "finishing_status"


class Circuit(models.Model):
    circuit_id = models.IntegerField(primary_key=True)
    circuit_ref = models.CharField(max_length=64)
    name = models.CharField(max_length=256)
    location = models.CharField(max_length=128)
    country = models.CharField(max_length=128)
    lat = models.FloatField(null=True)
    lng = models.FloatField(null=True)
    alt = models.SmallIntegerField(null=True)
    url = models.CharField(max_length=512)

    class Meta:
        managed = False
        db_table = "circuit"


class Driver(models.Model):
    driver_id = models.IntegerField(primary_key=True)
    driver_ref = models.CharField(max_length=64)
    driver_number = models.SmallIntegerField(null=True)
    code = models.CharField(max_length=8, null=True)
    forename = models.CharField(max_length=64)
    surname = models.CharField(max_length=64)
    dob = models.DateField(null=True)
    nationality = models.CharField(max_length=64)
    url = models.CharField(max_length=512)

    class Meta:
        managed = False
        db_table = "driver"


class Constructor(models.Model):
    constructor_id = models.IntegerField(primary_key=True)
    constructor_ref = models.CharField(max_length=64)
    name = models.CharField(max_length=128)
    nationality = models.CharField(max_length=64)
    url = models.CharField(max_length=512)

    class Meta:
        managed = False
        db_table = "constructor"


class Race(models.Model):
    race_id = models.IntegerField(primary_key=True)
    year = models.SmallIntegerField()
    round_num = models.SmallIntegerField()
    circuit = models.ForeignKey(Circuit, models.DO_NOTHING, db_column="circuit_id")
    name = models.CharField(max_length=256)
    race_date = models.DateField()
    race_time = models.TimeField(null=True)
    url = models.CharField(max_length=512)
    fp1_date = models.DateField(null=True)
    fp1_time = models.TimeField(null=True)
    fp2_date = models.DateField(null=True)
    fp2_time = models.TimeField(null=True)
    fp3_date = models.DateField(null=True)
    fp3_time = models.TimeField(null=True)
    quali_date = models.DateField(null=True)
    quali_time = models.TimeField(null=True)
    sprint_date = models.DateField(null=True)
    sprint_time = models.TimeField(null=True)

    class Meta:
        managed = False
        db_table = "race"


class RaceResult(models.Model):
    result_id = models.IntegerField(primary_key=True)
    race = models.ForeignKey(Race, models.DO_NOTHING, db_column="race_id")
    driver = models.ForeignKey(Driver, models.DO_NOTHING, db_column="driver_id")
    constructor = models.ForeignKey(Constructor, models.DO_NOTHING, db_column="constructor_id")
    car_number = models.SmallIntegerField(null=True)
    grid_pos = models.SmallIntegerField()
    finish_position = models.SmallIntegerField(null=True)
    position_text = models.CharField(max_length=32)
    position_order = models.SmallIntegerField()
    points = models.DecimalField(max_digits=5, decimal_places=2)
    laps = models.SmallIntegerField()
    finish_time = models.CharField(max_length=64, null=True)
    milliseconds = models.IntegerField(null=True)
    fastest_lap = models.SmallIntegerField(null=True)
    fastest_lap_rank = models.SmallIntegerField(null=True)
    fastest_lap_time = models.CharField(max_length=32, null=True)
    fastest_lap_speed = models.CharField(max_length=32, null=True)
    finishing_status = models.ForeignKey(
        FinishingStatus,
        models.DO_NOTHING,
        db_column="status_id",
        related_name="+",
    )

    class Meta:
        managed = False
        db_table = "race_result"


class QualifyingSession(models.Model):
    qualify_id = models.IntegerField(primary_key=True)
    race = models.ForeignKey(Race, models.DO_NOTHING, db_column="race_id")
    driver = models.ForeignKey(Driver, models.DO_NOTHING, db_column="driver_id")
    constructor = models.ForeignKey(Constructor, models.DO_NOTHING, db_column="constructor_id")
    car_number = models.SmallIntegerField(null=True)
    qualify_position = models.SmallIntegerField(null=True)
    q1 = models.CharField(max_length=32, null=True)
    q2 = models.CharField(max_length=32, null=True)
    q3 = models.CharField(max_length=32, null=True)

    class Meta:
        managed = False
        db_table = "qualifying_session"


class LapTime(models.Model):
    pk = models.CompositePrimaryKey("race_id", "driver_id", "lap_num")
    race_id = models.IntegerField()
    driver_id = models.IntegerField()
    lap_num = models.SmallIntegerField()
    lap_position = models.SmallIntegerField()
    lap_time = models.CharField(max_length=32)
    milliseconds = models.IntegerField()

    class Meta:
        managed = False
        db_table = "lap_time"


class LapReportingFact(models.Model):
    """Denormalised lap rows (same cardinality as `lap_time`) for reporting / rubric row-count."""

    fact_id = models.BigAutoField(primary_key=True)
    race = models.ForeignKey(Race, models.DO_NOTHING, db_column="race_id")
    driver = models.ForeignKey(Driver, models.DO_NOTHING, db_column="driver_id")
    lap_num = models.SmallIntegerField()
    lap_position = models.SmallIntegerField()
    lap_time = models.CharField(max_length=32)
    milliseconds = models.IntegerField()
    season_year = models.SmallIntegerField()
    grand_prix = models.CharField(max_length=256)
    circuit_country = models.CharField(max_length=128)
    driver_code = models.CharField(max_length=8, null=True)
    driver_surname = models.CharField(max_length=64)

    class Meta:
        managed = False
        db_table = "lap_reporting_fact"


class PitStop(models.Model):
    pk = models.CompositePrimaryKey("race_id", "driver_id", "stop_num")
    race_id = models.IntegerField()
    driver_id = models.IntegerField()
    stop_num = models.SmallIntegerField()
    lap_num = models.SmallIntegerField()
    clock_time = models.TimeField()
    duration = models.CharField(max_length=32)
    milliseconds = models.IntegerField()

    class Meta:
        managed = False
        db_table = "pit_stop"


class DriverStanding(models.Model):
    driver_standing_id = models.IntegerField(primary_key=True)
    race = models.ForeignKey(Race, models.DO_NOTHING, db_column="race_id")
    driver = models.ForeignKey(Driver, models.DO_NOTHING, db_column="driver_id")
    points = models.DecimalField(max_digits=7, decimal_places=2)
    championship_position = models.SmallIntegerField(null=True)
    position_text = models.CharField(max_length=32)
    wins = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = "driver_standing"


class ConstructorStanding(models.Model):
    constructor_standing_id = models.IntegerField(primary_key=True)
    race = models.ForeignKey(Race, models.DO_NOTHING, db_column="race_id")
    constructor = models.ForeignKey(Constructor, models.DO_NOTHING, db_column="constructor_id")
    points = models.DecimalField(max_digits=7, decimal_places=2)
    championship_position = models.SmallIntegerField(null=True)
    position_text = models.CharField(max_length=32)
    wins = models.SmallIntegerField()

    class Meta:
        managed = False
        db_table = "constructor_standing"


class ConstructorRaceResult(models.Model):
    constructor_result_id = models.IntegerField(primary_key=True)
    race = models.ForeignKey(Race, models.DO_NOTHING, db_column="race_id")
    constructor = models.ForeignKey(Constructor, models.DO_NOTHING, db_column="constructor_id")
    points = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    result_status = models.CharField(max_length=64, null=True)

    class Meta:
        managed = False
        db_table = "constructor_race_result"


class SprintResult(models.Model):
    sprint_result_id = models.IntegerField(primary_key=True)
    race = models.ForeignKey(Race, models.DO_NOTHING, db_column="race_id")
    driver = models.ForeignKey(Driver, models.DO_NOTHING, db_column="driver_id")
    constructor = models.ForeignKey(Constructor, models.DO_NOTHING, db_column="constructor_id")
    car_number = models.SmallIntegerField(null=True)
    grid_pos = models.SmallIntegerField()
    finish_position = models.SmallIntegerField(null=True)
    position_text = models.CharField(max_length=32)
    position_order = models.SmallIntegerField()
    points = models.DecimalField(max_digits=5, decimal_places=2)
    laps = models.SmallIntegerField()
    finish_time = models.CharField(max_length=64, null=True)
    milliseconds = models.IntegerField(null=True)
    fastest_lap = models.SmallIntegerField(null=True)
    fastest_lap_time = models.CharField(max_length=32, null=True)
    finishing_status = models.ForeignKey(
        FinishingStatus,
        models.DO_NOTHING,
        db_column="status_id",
        related_name="+",
    )

    class Meta:
        managed = False
        db_table = "sprint_result"


class RaceNote(models.Model):
    """Registered-user notes on a race (Django-managed; satisfies app-side CRUD)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="race_notes",
    )
    race_id = models.PositiveIntegerField()
    body = models.TextField(max_length=2048)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "racing_race_note"
        ordering = ["-updated_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"note#{self.pk} race={self.race_id}"
