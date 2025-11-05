from django.urls import path
from .views import ShipmentListView, ShipmentDetailView, ShipmentCreateView

app_name = "shipments"
urlpatterns = [
    path("", ShipmentListView.as_view(), name="list"),
    path("new/", ShipmentCreateView.as_view(), name="create"),
    path("<int:pk>/", ShipmentDetailView.as_view(), name="detail"),
]
