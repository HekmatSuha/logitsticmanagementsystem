from django.contrib import messages
from django.db.models import Case, F, IntegerField, Q, When
from django.urls import reverse_lazy, reverse
from urllib.parse import urlencode
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import FormMixin

from .forms import ShipmentForm, ShipmentEventForm
from .models import Shipment


class ShipmentListView(ListView):
    template_name = "shipments/list.html"
    model = Shipment
    context_object_name = "shipments"

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related("events")
        tab = self.request.GET.get("tab", "active")
        if tab == "completed":
            queryset = queryset.filter(status="delivered")
        else:
            queryset = queryset.exclude(status="delivered")

        status_filter = self.request.GET.get("status", "all")
        if status_filter != "all":
            queryset = queryset.filter(status=status_filter)

        priority_filter = self.request.GET.get("priority", "all")
        if priority_filter != "all":
            queryset = queryset.filter(priority=priority_filter)

        search = self.request.GET.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(tracking_id__icontains=search)
                | Q(origin__icontains=search)
                | Q(destination__icontains=search)
                | Q(carrier__icontains=search)
                | Q(contents__icontains=search)
            )

        sort = self.request.GET.get("sort", "eta")
        if sort == "priority":
            queryset = queryset.annotate(
                priority_rank=Case(
                    When(priority="high", then=0),
                    When(priority="medium", then=1),
                    When(priority="low", then=2),
                    default=3,
                    output_field=IntegerField(),
                )
            ).order_by("priority_rank", F("eta").asc(nulls_last=True), "tracking_id")
        else:
            order_expression = {
                "eta": F("eta").asc(nulls_last=True),
                "eta_desc": F("eta").desc(nulls_last=True),
                "updated": F("last_updated").desc(nulls_last=True),
            }.get(sort, F("eta").asc(nulls_last=True))
            queryset = queryset.order_by(order_expression, "tracking_id")
        return queryset

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tab = self.request.GET.get("tab", "active")
        selected = None
        sel = self.request.GET.get("id")
        object_list = list(ctx["shipments"])
        if sel:
            selected = next((s for s in object_list if str(s.pk) == sel), None)
        if not selected and object_list:
            selected = object_list[0]
        status_choices_active = [("all", "Status: All")] + [
            (value, label)
            for value, label in Shipment.STATUS_CHOICES
            if value != "delivered"
        ]
        status_choices_completed = [("all", "Status: All")] + list(Shipment.STATUS_CHOICES)

        ctx.update(
            {
                "selected": selected,
                "current_tab": tab,
                "status_filter": self.request.GET.get("status", "all"),
                "priority_filter": self.request.GET.get("priority", "all"),
                "sort_option": self.request.GET.get("sort", "eta"),
                "search_query": self.request.GET.get("q", "").strip(),
                "active_count": Shipment.objects.exclude(status="delivered").count(),
                "completed_count": Shipment.objects.filter(status="delivered").count(),
                "status_choices_active": status_choices_active,
                "status_choices_completed": status_choices_completed,
                "status_choices_current": status_choices_completed if tab == "completed" else status_choices_active,
                "priority_choices": [("all", "Priority: All")] + list(Shipment.PRIORITY_CHOICES),
                "sort_choices": [
                    ("eta", "Sort by: ETA (Soonest)"),
                    ("eta_desc", "Sort by: ETA (Latest)"),
                    ("updated", "Sort by: Last Updated"),
                    ("priority", "Sort by: Priority"),
                ],
                "quick_filters": [
                    {
                        "label": "Delayed shipments",
                        "query": urlencode({"tab": "active", "status": "delayed"}),
                    },
                    {
                        "label": "High priority",
                        "query": urlencode({"tab": "active", "priority": "high"}),
                    },
                    {
                        "label": "Delivered this week",
                        "query": urlencode({"tab": "completed", "sort": "eta_desc"}),
                    },
                ],
            }
        )
        return ctx


class ShipmentCreateView(CreateView):
    template_name = "shipments/create.html"
    model = Shipment
    form_class = ShipmentForm
    success_url = reverse_lazy("shipments:list")

    def form_valid(self, form):
        messages.success(self.request, "Shipment created successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the highlighted errors.")
        return super().form_invalid(form)


class ShipmentDetailView(FormMixin, DetailView):
    template_name = "shipments/detail.html"
    queryset = Shipment.objects.prefetch_related("events")
    form_class = ShipmentEventForm

    def get_success_url(self):
        return reverse("shipments:detail", args=[self.object.pk])

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            event = form.save(commit=False)
            event.shipment = self.object
            event.save()
            messages.success(request, "Transit event added.")
            return super().form_valid(form)
        messages.error(request, "Unable to add event. Please fix the errors below.")
        return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event_form = kwargs.get("event_form") if "event_form" in kwargs else None
        context["event_form"] = event_form or self.get_form()
        return context

    def form_invalid(self, form):
        context = self.get_context_data(event_form=form)
        return self.render_to_response(context)
