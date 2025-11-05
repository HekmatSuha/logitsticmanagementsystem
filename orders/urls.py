from django.urls import path
from .views import OrderListView, OrderCreateView, OrderInvoiceView

app_name = "orders"
urlpatterns = [
    path("", OrderListView.as_view(), name="list"),
    path("new/", OrderCreateView.as_view(), name="create"),
    path("<int:pk>/invoice/", OrderInvoiceView.as_view(), name="invoice"),
]
