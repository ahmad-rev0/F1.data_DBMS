from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.F1LoginView.as_view(), name="login"),
    path("logout/", views.F1LogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
]
