from urllib.parse import urlencode

from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, DetailView

from .forms import OrderForm
from .models import Order


class OrderListView(ListView):
    template_name = "orders/list.html"
    model = Order
    context_object_name = "orders"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().order_by("-order_date", "-pk")
        query = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "all")
        if query:
            queryset = queryset.filter(
                Q(customer_name__icontains=query) | Q(pk__icontains=query)
            )
        if status != "all":
            queryset = queryset.filter(status=status)
        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        search_query = self.request.GET.get("q", "").strip()
        status_filter = self.request.GET.get("status", "all")
        orders_list = list(ctx["orders"])
        selected = None
        selected_id = self.request.GET.get("id")
        if selected_id:
            selected = next((order for order in orders_list if str(order.pk) == selected_id), None)
        if not selected and orders_list:
            selected = orders_list[0]
        history = []
        if selected:
            history.append(
                {
                    "label": "Order Created",
                    "timestamp": selected.order_date,
                    "description": "Order placed by customer",
                }
            )
            if selected.status in {"processing", "delivered", "cancelled"}:
                history.append(
                    {
                        "label": "Payment Received",
                        "timestamp": selected.order_date,
                        "description": "Payment confirmed",
                    }
                )
            if selected.status in {"processing", "delivered"}:
                history.append(
                    {
                        "label": "Shipped",
                        "timestamp": selected.order_date,
                        "description": "Shipment dispatched",
                    }
                )
            if selected.status == "delivered":
                history.append(
                    {
                        "label": "Delivered",
                        "timestamp": selected.order_date,
                        "description": "Shipment delivered to customer",
                    }
                )
        ctx.update(
            {
                "search_query": search_query,
                "status_filter": status_filter,
                "status_options": [("all", "Status: All")] + list(Order.STATUS_CHOICES),
                "selected": selected,
                "selected_history": history,
                "quick_filters": [
                    {"label": "Pending", "query": urlencode({"status": "pending"})},
                    {"label": "Processing", "query": urlencode({"status": "processing"})},
                    {"label": "Delivered", "query": urlencode({"status": "delivered"})},
                ],
            }
        )
        return ctx


class OrderCreateView(CreateView):
    template_name = "orders/create.html"
    model = Order
    form_class = OrderForm
    success_url = reverse_lazy("orders:list")

    def form_valid(self, form):
        messages.success(self.request, "Order created successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class OrderInvoiceView(DetailView):
    model = Order
    template_name = "orders/invoice.html"
    context_object_name = "order"
