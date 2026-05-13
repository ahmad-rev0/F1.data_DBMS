from __future__ import annotations

from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import FanSignupForm


class F1LoginView(LoginView):
    template_name = "accounts/login.html"


class F1LogoutView(LogoutView):
    next_page = reverse_lazy("core:home")


def register(request):
    if request.user.is_authenticated:
        return redirect("core:home")
    if request.method == "POST":
        form = FanSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("core:home")
    else:
        form = FanSignupForm()
    return render(request, "accounts/register.html", {"form": form})
