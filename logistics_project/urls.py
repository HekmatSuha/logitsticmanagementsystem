from django.contrib import admin
from django.urls import path, include
from core.views import DashboardView, global_search, healthcheck
from users.views import CustomLoginView, RegisterView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", DashboardView.as_view(), name="dashboard"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("search/", global_search, name="global_search"),
    path("health/", healthcheck, name="health"),
    path("shipments/", include("shipments.urls")),
    path("inventory/", include("inventory.urls")),
    path("orders/", include("orders.urls")),
    path("reports/", include("reports.urls")),
    path("users/", include("users.urls")),
]
