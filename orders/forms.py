from django import forms

from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["customer_name", "order_date", "total_amount", "status"]
        widgets = {
            "customer_name": forms.TextInput(
                attrs={
                    "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
                    "placeholder": "Customer name",
                }
            ),
            "order_date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
                }
            ),
            "total_amount": forms.NumberInput(
                attrs={
                    "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
                    "min": "0",
                    "step": "0.01",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-select rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
                }
            ),
        }
