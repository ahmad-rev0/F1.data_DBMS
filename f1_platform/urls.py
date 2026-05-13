from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("api/", include("racing.urls_api")),
    path("", include(("core.urls", "core"), namespace="core")),
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("", include(("racing.urls", "racing"), namespace="racing")),
    path("admin-panel/", include(("admin_panel.urls", "admin_panel"), namespace="admin_panel")),
]
