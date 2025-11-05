from django.contrib import admin
from django.urls import path, include
from core.views import DashboardView, healthcheck

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", DashboardView.as_view(), name="dashboard"),
    path("health/", healthcheck, name="health"),
    path("shipments/", include("shipments.urls")),
    path("inventory/", include("inventory.urls")),
    path("orders/", include("orders.urls")),
    path("reports/", include("reports.urls")),
    path("users/", include("users.urls")),
]
