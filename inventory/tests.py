from django.test import TestCase
from django.urls import reverse

from .models import Warehouse, Product, StockItem


class InventoryListViewTests(TestCase):
    def setUp(self):
        self.warehouse = Warehouse.objects.create(name="Central Hub")
        self.product_a = Product.objects.create(name="Widget Alpha", sku="W-A", reorder_point=5)
        self.product_b = Product.objects.create(name="Gadget Beta", sku="G-B", reorder_point=15)
        StockItem.objects.create(product=self.product_a, warehouse=self.warehouse, quantity=2)
        StockItem.objects.create(product=self.product_b, warehouse=self.warehouse, quantity=20)

    def test_search_filters_items_by_name_or_sku(self):
        url = reverse("inventory:list")
        response = self.client.get(url, {"q": "widget"})
        self.assertEqual(response.status_code, 200)
        items = list(response.context["items"])
        self.assertEqual(len(items), 1, "Search should return only matching stock items")
        self.assertEqual(items[0].product, self.product_a)

    def test_create_item_with_existing_product_and_warehouse(self):
        url = reverse("inventory:create")
        response = self.client.post(
            url,
            {
                "product": self.product_a.id,
                "warehouse": self.warehouse.id,
                "quantity": 15,
            },
        )
        self.assertRedirects(response, reverse("inventory:list"))
        item = StockItem.objects.get(product=self.product_a, warehouse=self.warehouse)
        self.assertEqual(item.quantity, 15)

    def test_create_item_with_new_product_and_warehouse(self):
        url = reverse("inventory:create")
        response = self.client.post(
            url,
            {
                "new_product_name": "Widget Gamma",
                "new_product_sku": "W-G",
                "new_product_reorder_point": 8,
                "new_warehouse_name": "North Hub",
                "new_warehouse_location": "Astana",
                "quantity": 5,
            },
        )
        self.assertRedirects(response, reverse("inventory:list"))
        product = Product.objects.get(sku="W-G")
        warehouse = Warehouse.objects.get(name="North Hub")
        item = StockItem.objects.get(product=product, warehouse=warehouse)
        self.assertEqual(item.quantity, 5)
