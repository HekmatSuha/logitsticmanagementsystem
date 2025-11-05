from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Order


class OrderListViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="orders", password="test-pass"
        )
        self.client.login(username="orders", password="test-pass")
        self.recent = Order.objects.create(
            customer_name="Jane Smith",
            order_date=date(2024, 10, 25),
            total_amount=150.50,
            status="processing",
        )
        self.older = Order.objects.create(
            customer_name="John Doe",
            order_date=date(2024, 10, 20),
            total_amount=250,
            status="delivered",
        )

    def test_list_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("orders:list"))
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('orders:list')}",
        )

    def test_search_filters_by_customer_name(self):
        response = self.client.get(reverse("orders:list"), {"q": "Jane"})
        self.assertContains(response, self.recent.customer_name)
        self.assertNotContains(response, self.older.customer_name)

    def test_selected_order_defaults_to_first_result(self):
        response = self.client.get(reverse("orders:list"))
        selected = response.context["selected"]
        self.assertIsNotNone(selected)
        self.assertEqual(selected.pk, self.recent.pk)

    def test_create_order_via_form(self):
        response = self.client.post(
            reverse("orders:create"),
            {
                "customer_name": "Acme Corp",
                "order_date": "2024-10-28",
                "total_amount": "199.99",
                "status": "pending",
            },
        )
        self.assertRedirects(response, reverse("orders:list"))
        self.assertTrue(Order.objects.filter(customer_name="Acme Corp").exists())

    def test_invoice_requires_login(self):
        self.client.logout()
        url = reverse("orders:invoice", args=[self.recent.pk])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('login')}?next={url}")
