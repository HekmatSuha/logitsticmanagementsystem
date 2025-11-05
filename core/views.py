import json

from django.http import HttpResponse
from django.shortcuts import render
from datetime import timedelta

from django.db.models import Count, F, Q, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.views.generic import TemplateView
from urllib.parse import urlencode

from inventory.models import StockItem
from orders.models import Order
from shipments.models import Shipment


class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        now = timezone.now()

        timeframe_options = [
            {"label": "Today", "value": "today", "delta": timedelta(days=1)},
            {"label": "Last 7 Days", "value": "7d", "delta": timedelta(days=7)},
            {"label": "This Month", "value": "month", "delta": timedelta(days=30)},
        ]
        active_key = self.request.GET.get("range", "7d")
        selected_timeframe = next((tf for tf in timeframe_options if tf["value"] == active_key), timeframe_options[1])
        delta = selected_timeframe["delta"]
        date_from = now - delta
        previous_from = date_from - delta

        shipments = Shipment.objects.all()
        orders = Order.objects.all()
        stock_items = StockItem.objects.select_related("product", "warehouse")

        shipments_current = shipments.filter(last_updated__gte=date_from)
        shipments_previous = shipments.filter(last_updated__gte=previous_from, last_updated__lt=date_from)

        orders_current = orders.filter(order_date__gte=date_from.date())
        orders_previous = orders.filter(order_date__gte=previous_from.date(), order_date__lt=date_from.date())

        def format_number(value):
            return f"{value:,}"

        def calc_delta(current, previous):
            if previous > 0:
                change = ((current - previous) / previous) * 100
            else:
                change = 100.0 if current > 0 else 0.0
            tone = "success" if change > 0 else "danger"
            if abs(change) < 0.0001:
                tone = "warning"
            return f"{change:+.1f}%", tone

        def calc_percent_delta(current, previous):
            change = current - previous
            tone = "success" if change > 0 else "danger"
            if abs(change) < 0.0001:
                tone = "warning"
            return f"{change:+.1f}%", tone

        active_shipments_count = shipments.exclude(status="delivered").count()
        active_shipments_current = shipments_current.exclude(status="delivered").count()
        active_shipments_previous = shipments_previous.exclude(status="delivered").count()
        active_shipments_delta, active_shipments_tone = calc_delta(active_shipments_current, active_shipments_previous)

        pending_orders_count = Order.objects.filter(status="pending").count()
        pending_orders_current = orders_current.filter(status="pending").count()
        pending_orders_previous = orders_previous.filter(status="pending").count()
        pending_orders_delta, pending_orders_tone = calc_delta(pending_orders_current, pending_orders_previous)

        shipments_total = shipments.count()
        on_time_count = shipments.filter(status__in=["on_time", "delivered"]).count()
        on_time_previous_total = shipments_previous.count()
        on_time_previous_count = shipments_previous.filter(status__in=["on_time", "delivered"]).count()
        on_time_pct = (on_time_count / shipments_total * 100) if shipments_total else 0.0
        on_time_previous_pct = (on_time_previous_count / on_time_previous_total * 100) if on_time_previous_total else 0.0
        on_time_delta, on_time_tone = calc_percent_delta(on_time_pct, on_time_previous_pct)

        total_units = stock_items.aggregate(total=Sum("quantity"))["total"] or 0
        low_stock_count = stock_items.filter(quantity__gt=0, quantity__lte=F("product__reorder_point")).count()
        out_of_stock_count = stock_items.filter(quantity__lte=0).count()

        stats = [
            {
                "label": "Active Shipments",
                "value": format_number(active_shipments_count),
                "delta": active_shipments_delta,
                "tone": active_shipments_tone,
            },
            {
                "label": "Pending Orders",
                "value": format_number(pending_orders_count),
                "delta": pending_orders_delta,
                "tone": pending_orders_tone,
            },
            {
                "label": "On-Time Delivery",
                "value": f"{on_time_pct:.1f}%",
                "delta": on_time_delta,
                "tone": on_time_tone,
            },
            {
                "label": "Inventory Units",
                "value": format_number(total_units),
                "delta": "+0.0%",
                "tone": "warning",
            },
        ]

        shipment_volume_raw = (
            shipments_current.annotate(day=TruncDate("last_updated"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        shipment_volume_max = max([item["count"] for item in shipment_volume_raw], default=1)
        shipment_volume = [
            {
                "label": item["day"].strftime("%b %d"),
                "count": item["count"],
                "percent": int(item["count"] / shipment_volume_max * 100) if shipment_volume_max else 0,
            }
            for item in shipment_volume_raw
        ]

        shipment_volume_labels = [item["label"] for item in shipment_volume]
        shipment_volume_data = [item["count"] for item in shipment_volume]


        in_stock_count = stock_items.filter(quantity__gt=F("product__reorder_point")).count()
        inventory_status_total = in_stock_count + low_stock_count + out_of_stock_count or 1
        inventory_status = [
            {
                "label": "In Stock",
                "count": in_stock_count,
                "percent": int(in_stock_count / inventory_status_total * 100),
                "color": "bg-success",
            },
            {
                "label": "Low Stock",
                "count": low_stock_count,
                "percent": int(low_stock_count / inventory_status_total * 100),
                "color": "bg-warning",
            },
            {
                "label": "Out of Stock",
                "count": out_of_stock_count,
                "percent": int(out_of_stock_count / inventory_status_total * 100),
                "color": "bg-danger",
            },
        ]

        alerts = []
        delayed_shipments = shipments.filter(status__in=["delayed", "issue"]).order_by("-last_updated")[:3]
        for shipment in delayed_shipments:
            alerts.append(
                {
                    "level": "danger",
                    "icon": "warning",
                    "message": f"Shipment {shipment.tracking_id} is {shipment.get_status_display().lower()}",
                    "detail": f"{shipment.origin} → {shipment.destination}",
                    "timestamp": shipment.last_updated,
                }
            )

        low_stock_items = stock_items.filter(quantity__gt=0, quantity__lte=F("product__reorder_point")).order_by("quantity")[:3]
        for item in low_stock_items:
            alerts.append(
                {
                    "level": "warning",
                    "icon": "inventory_2",
                    "message": f"Low stock: {item.product.name}",
                    "detail": f"{item.quantity} units at {item.warehouse.name}",
                    "timestamp": now,
                }
            )

        overdue_orders = orders.filter(status="pending", order_date__lt=now.date() - timedelta(days=3)).order_by("order_date")[:2]
        for order in overdue_orders:
            alerts.append(
                {
                    "level": "info",
                    "icon": "shopping_cart",
                    "message": f"Order #{order.pk} pending since {order.order_date:%b %d}",
                    "detail": order.customer_name,
                    "timestamp": now,
                }
            )

        status_labels = dict(Shipment.STATUS_CHOICES)
        status_overview_raw = shipments.values("status").annotate(count=Count("id")).order_by("-count")
        status_overview = [
            {"label": status_labels.get(row["status"], row["status"]), "count": row["count"]}
            for row in status_overview_raw
        ]

        sort_by = self.request.GET.get("sort", "order_date")
        sort_dir = self.request.GET.get("dir", "desc")
        sort_dir_prefix = "" if sort_dir == "asc" else "-"

        valid_sort_fields = ["pk", "customer_name", "order_date", "total_amount", "status"]
        if sort_by not in valid_sort_fields:
            sort_by = "order_date"

        recent_orders = orders.order_by(f"{sort_dir_prefix}{sort_by}")[:5]

        base_query = self.request.GET.copy()
        timeframes = []
        for option in timeframe_options:
            params = base_query.copy()
            params["range"] = option["value"]
            option = option.copy()
            option["url"] = f"?{urlencode(params)}"
            timeframes.append(option)

        ctx.update(
            {
                "timeframes": timeframes,
                "active_timeframe": selected_timeframe["value"],
                "stats": stats,
                "shipment_volume": shipment_volume,
                "shipment_volume_labels": json.dumps(shipment_volume_labels),
                "shipment_volume_data": json.dumps(shipment_volume_data),
                "inventory_status": inventory_status,
                "alerts": alerts,
                "status_overview": status_overview,
                "recent_orders": recent_orders,
                "sort_by": sort_by,
                "sort_dir": sort_dir,
            }
        )
        return ctx


def healthcheck(request):
    return HttpResponse("ok")


def global_search(request):
    query = request.GET.get("q", "").strip()

    shipments = []
    orders = []
    inventory_items = []
    total_results = 0

    if query:
        shipment_filters = Q(tracking_id__icontains=query) | Q(origin__icontains=query) | Q(
            destination__icontains=query
        ) | Q(carrier__icontains=query) | Q(contents__icontains=query)
        shipments = list(
            Shipment.objects.filter(shipment_filters).order_by("-last_updated")[:25]
        )

        order_filters = Q(customer_name__icontains=query) | Q(status__icontains=query)
        if query.isdigit():
            order_filters |= Q(pk=int(query))
        orders = list(Order.objects.filter(order_filters).order_by("-order_date")[:25])

        inventory_filters = (
            Q(product__name__icontains=query)
            | Q(product__sku__icontains=query)
            | Q(warehouse__name__icontains=query)
        )
        inventory_items = list(
            StockItem.objects.select_related("product", "warehouse")
            .filter(inventory_filters)
            .order_by("product__name")[:25]
        )

        total_results = len(shipments) + len(orders) + len(inventory_items)

    context = {
        "query": query,
        "shipments": shipments,
        "orders": orders,
        "inventory_items": inventory_items,
        "total_results": total_results,
        "has_query": bool(query),
    }

    return render(request, "search_results.html", context)
