from django import forms
from django.core.exceptions import ValidationError

from .models import Product, StockItem, Warehouse


class InventoryItemForm(forms.Form):
    product = forms.ModelChoiceField(
        queryset=Product.objects.all().order_by("name"),
        required=False,
        label="Existing product",
        widget=forms.Select(
            attrs={
                "class": "form-select rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
            }
        ),
    )
    new_product_name = forms.CharField(
        required=False,
        label="New product name",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Product name",
                "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
            }
        ),
    )
    new_product_sku = forms.CharField(
        required=False,
        label="New product SKU",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Unique SKU",
                "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
            }
        ),
    )
    new_product_reorder_point = forms.IntegerField(
        required=False,
        min_value=0,
        label="Reorder point",
        widget=forms.NumberInput(
            attrs={
                "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
            }
        ),
    )

    warehouse = forms.ModelChoiceField(
        queryset=Warehouse.objects.all().order_by("name"),
        required=False,
        label="Existing warehouse",
        widget=forms.Select(
            attrs={
                "class": "form-select rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
            }
        ),
    )
    new_warehouse_name = forms.CharField(
        required=False,
        label="New warehouse name",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Warehouse name",
                "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
            }
        ),
    )
    new_warehouse_location = forms.CharField(
        required=False,
        label="Warehouse location",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Location (optional)",
                "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
            }
        ),
    )

    quantity = forms.IntegerField(
        min_value=0,
        label="Quantity",
        widget=forms.NumberInput(
            attrs={
                "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
            }
        ),
    )

    def clean(self):
        cleaned = super().clean()
        product = cleaned.get("product")
        warehouse = cleaned.get("warehouse")
        new_product_name = cleaned.get("new_product_name")
        new_product_sku = cleaned.get("new_product_sku")
        new_warehouse_name = cleaned.get("new_warehouse_name")

        if not product and not (new_product_name and new_product_sku):
            raise ValidationError("Select an existing product or provide details for a new one.")

        if product and (new_product_name or new_product_sku):
            raise ValidationError("Choose either an existing product or enter a new product, not both.")

        if not warehouse and not new_warehouse_name:
            raise ValidationError("Select an existing warehouse or provide a name for a new one.")

        if warehouse and new_warehouse_name:
            raise ValidationError("Choose either an existing warehouse or enter a new warehouse, not both.")

        return cleaned

    def save(self):
        cleaned = self.cleaned_data

        product = cleaned.get("product")
        if not product:
            product, _ = Product.objects.get_or_create(
                sku=cleaned["new_product_sku"],
                defaults={
                    "name": cleaned["new_product_name"],
                    "reorder_point": cleaned.get("new_product_reorder_point") or 0,
                },
            )

        warehouse = cleaned.get("warehouse")
        if not warehouse:
            warehouse, _ = Warehouse.objects.get_or_create(
                name=cleaned["new_warehouse_name"],
                defaults={"location": cleaned.get("new_warehouse_location", "")},
            )

        quantity = cleaned["quantity"]
        stock_item, created = StockItem.objects.get_or_create(
            product=product,
            warehouse=warehouse,
            defaults={"quantity": quantity},
        )
        if not created:
            stock_item.quantity = quantity
            stock_item.save(update_fields=["quantity"])

        return stock_item
