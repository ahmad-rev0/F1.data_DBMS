from __future__ import annotations

from django import forms

from .models import RaceNote


class RaceNoteForm(forms.ModelForm):
    class Meta:
        model = RaceNote
        fields = ("body",)
        widgets = {"body": forms.Textarea(attrs={"rows": 3, "class": "form-control"})}


class RaceResultPointsForm(forms.Form):
    points = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control form-control-sm", "step": "0.5"}),
    )
