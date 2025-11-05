from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Shipment, ShipmentEvent


class ShipmentListViewTests(TestCase):
    def setUp(self):
        self.active_shipment = Shipment.objects.create(
            tracking_id="TRACK123",
            origin="New York, NY",
            destination="Los Angeles, CA",
            status="in_transit",
            priority="high",
            eta=timezone.now() + timezone.timedelta(days=2),
        )
        ShipmentEvent.objects.create(
            shipment=self.active_shipment,
            timestamp=timezone.now(),
            description="Out for delivery",
            location="New York, NY",
        )

        self.delivered_shipment = Shipment.objects.create(
            tracking_id="TRACK999",
            origin="Chicago, IL",
            destination="Seattle, WA",
            status="delivered",
            priority="low",
            eta=timezone.now() - timezone.timedelta(days=1),
        )

    def test_route_uses_html_arrow_entity(self):
        response = self.client.get(reverse("shipments:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "New York, NY &rarr; Los Angeles, CA")

    def test_active_tab_excludes_delivered_shipments(self):
        response = self.client.get(reverse("shipments:list"))
        self.assertContains(response, self.active_shipment.tracking_id)
        self.assertNotContains(response, self.delivered_shipment.tracking_id)

    def test_completed_tab_shows_delivered_shipments(self):
        response = self.client.get(reverse("shipments:list"), {"tab": "completed"})
        self.assertContains(response, self.delivered_shipment.tracking_id)
        self.assertNotContains(response, self.active_shipment.tracking_id)

    def test_search_filters_shipments(self):
        response = self.client.get(reverse("shipments:list"), {"q": "123"})
        self.assertContains(response, self.active_shipment.tracking_id)
        self.assertNotContains(response, self.delivered_shipment.tracking_id)

    def test_selected_shipment_shows_transit_history(self):
        response = self.client.get(reverse("shipments:list"), {"id": self.active_shipment.id})
        self.assertContains(response, "Out for delivery")
        self.assertContains(response, self.active_shipment.tracking_id)

    def test_create_shipment_via_form(self):
        eta = timezone.now() + timezone.timedelta(days=3)
        departure = timezone.now()
        response = self.client.post(
            reverse("shipments:create"),
            {
                "tracking_id": "TRACK777",
                "origin": "Austin, TX",
                "destination": "Phoenix, AZ",
                "eta": eta.strftime("%Y-%m-%dT%H:%M"),
                "status": "in_transit",
                "priority": "medium",
                "carrier": "FedEx",
                "contents": "Electronics",
                "driver_contact": "555-9876",
                "departure_time": departure.strftime("%Y-%m-%dT%H:%M"),
            },
        )
        self.assertRedirects(response, reverse("shipments:list"))
        self.assertTrue(Shipment.objects.filter(tracking_id="TRACK777").exists())

    def test_add_event_via_detail_form(self):
        timestamp = timezone.now()
        url = reverse("shipments:detail", args=[self.active_shipment.id])
        response = self.client.post(
            url,
            {
                "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M"),
                "description": "Arrived at facility",
                "location": "Las Vegas, NV",
                "icon": "warehouse",
            },
        )
        self.assertRedirects(response, url)
        self.assertTrue(
            self.active_shipment.events.filter(description="Arrived at facility").exists()
        )
