from django.urls import path
from .views import InventoryListView, InventoryDetailView, InventoryCreateView, inventory_bulk_action

app_name = "inventory"
urlpatterns = [
    path("", InventoryListView.as_view(), name="list"),
    path("<int:pk>/", InventoryDetailView.as_view(), name="detail"),
    path("new/", InventoryCreateView.as_view(), name="create"),
    path("bulk-action/", inventory_bulk_action, name="bulk_action"),
]
