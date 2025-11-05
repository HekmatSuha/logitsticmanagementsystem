from datetime import date

from django.views.generic import TemplateView


class ReportsIndexView(TemplateView):
    template_name = "reports/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        selected_report = self.request.GET.get("report", "Shipment Performance")
        selected_date = self.request.GET.get("date", date.today().isoformat())
        ctx.update(
            {
                "report_types": [
                    "Shipment Performance",
                    "Inventory Turnover",
                    "Delivery Success",
                    "Cost Analysis",
                ],
                "selected_report": selected_report,
                "selected_date": selected_date,
                "filters": [
                    {"key": "carrier", "label": "By Carrier", "checked": False},
                    {"key": "warehouse", "label": "By Warehouse", "checked": True},
                    {"key": "status", "label": "By Status", "checked": False},
                ],
                "metrics": [
                    {"label": "Total Shipments", "value": "1,428", "trend": "+5.4%"},
                    {"label": "Delivery Success", "value": "98.2%", "trend": "+0.8%"},
                    {"label": "Inventory Turnover", "value": "6.4", "trend": "-2.1%"},
                    {"label": "Avg. Transit Time", "value": "3.1 Days", "trend": "+1.2%"},
                ],
                "chart_image": "https://lh3.googleusercontent.com/aida-public/AB6AXuB1rXRU6lJG8SQDP3rI6jylTepokG2ZbG7-86vEfnjLp4bERxmaDatOW3kzG8d8rA81Z5Zda7e3yfmyGi84R1QPtOXi1py0LqJvEdp9zewKYCVjS-BW-N-GPXCFoVbc--ccIiNY8t_nzVIPk1u0nKkIYv4I67SP2q-DbWlPeMrprv8fPUrbV42y3Bj8irHCqXKWl5sXAwgLYWlgcF63uHXr9UtozxQx_tX7Pj0Tv65284IU3aszfMilZwpRkZBHMAkZf-ePkhrzEg",
            }
        )
        return ctx
