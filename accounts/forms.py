from __future__ import annotations

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class FanSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    favourite_team = forms.CharField(
        max_length=64,
        required=False,
        help_text="Optional — e.g. favourite constructor name.",
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "favourite_team")

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            Profile.objects.filter(user=user).update(
                favourite_team=self.cleaned_data.get("favourite_team", ""),
            )
        return user
