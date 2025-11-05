from django.contrib import messages
from django.db.models import F, Q, Sum
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, FormView

from .forms import InventoryItemForm
from .models import StockItem


class InventoryListView(ListView):
    template_name = "inventory/list.html"
    model = StockItem
    context_object_name = "items"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related("product", "warehouse")
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(product__name__icontains=query) | Q(product__sku__icontains=query)
            )
        return queryset.order_by("product__name", "warehouse__name")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        total_items = StockItem.objects.count()
        low_stock_count = StockItem.objects.filter(
            quantity__lte=F("product__reorder_point")
        ).count()
        total_units = (
            StockItem.objects.aggregate(total_units=Sum("quantity"))["total_units"] or 0
        )
        gradients = [
            "from-purple-500 to-violet-600",
            "from-sky-500 to-cyan-600",
            "from-emerald-500 to-lime-600",
        ]
        stats = [
            {
                "label": "Total Items",
                "value": f"{total_items:,}",
                "change": "+0.0%",
                "tone": "success",
            },
            {
                "label": "Items with Low Stock",
                "value": f"{low_stock_count:,}",
                "change": "+0.0%",
                "tone": "danger",
            },
            {
                "label": "Total Units Available",
                "value": f"{total_units:,}",
                "change": "+0.0%",
                "tone": "success",
            },
        ]

        for stat, gradient in zip(stats, gradients):
            stat["gradient"] = gradient

        ctx.update(
            {
                "search_query": self.request.GET.get("q", "").strip(),
                "stats": stats,
            }
        )
        return ctx


class InventoryDetailView(DetailView):
    template_name = "inventory/detail.html"
    model = StockItem


class InventoryCreateView(FormView):
    template_name = "inventory/create.html"
    success_url = reverse_lazy("inventory:list")
    form_class = InventoryItemForm

    def form_valid(self, form):
        stock_item = form.save()
        messages.success(
            self.request,
            f"Inventory updated for {stock_item.product.name} at {stock_item.warehouse.name}.",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the highlighted errors.")
        return super().form_invalid(form)


@require_POST
def inventory_bulk_action(request):
    action = request.POST.get("action")
    selected_items = request.POST.getlist("selected_items")

    if not selected_items:
        messages.error(request, "You must select at least one item.")
        return redirect("inventory:list")

    if action == "delete":
        queryset = StockItem.objects.filter(id__in=selected_items)
        count = queryset.count()
        queryset.delete()
        messages.success(request, f"Successfully deleted {count} inventory item(s).")
    else:
        messages.error(request, "Invalid bulk action.")

    return redirect("inventory:list")