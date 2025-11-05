from django import forms

from .models import Shipment, ShipmentEvent


class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = [
            "tracking_id",
            "origin",
            "destination",
            "eta",
            "status",
            "priority",
            "carrier",
            "contents",
            "driver_contact",
            "departure_time",
        ]
        widgets = {
            "tracking_id": forms.TextInput(
                attrs={
                    "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
                    "placeholder": "Tracking ID",
                }
            ),
            "origin": forms.TextInput(
                attrs={
                    "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
                    "placeholder": "Origin city, state",
                }
            ),
            "destination": forms.TextInput(
                attrs={
                    "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
                    "placeholder": "Destination city, state",
                }
            ),
            "eta": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
                }
            ),
            "status": forms.Select(
                attrs={
                    "class": "form-select rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
                }
            ),
            "priority": forms.Select(
                attrs={
                    "class": "form-select rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
                }
            ),
            "carrier": forms.TextInput(
                attrs={
                    "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
                    "placeholder": "Carrier name",
                }
            ),
            "contents": forms.TextInput(
                attrs={
                    "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
                    "placeholder": "Summary of goods",
                }
            ),
            "driver_contact": forms.TextInput(
                attrs={
                    "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
                    "placeholder": "Driver contact",
                }
            ),
            "departure_time": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
                }
            ),
        }


class ShipmentEventForm(forms.ModelForm):
    class Meta:
        model = ShipmentEvent
        fields = ["timestamp", "description", "location", "icon"]
        widgets = {
            "timestamp": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
                }
            ),
            "description": forms.TextInput(
                attrs={
                    "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
                    "placeholder": "Event description",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
                    "placeholder": "Location (optional)",
                }
            ),
            "icon": forms.TextInput(
                attrs={
                    "class": "form-input rounded-lg border border-border-light bg-card-light px-3 py-2 text-text-light focus:outline-none focus:ring-2 focus:ring-primary/50 dark:border-border-dark dark:bg-card-dark dark:text-text-dark",
                    "placeholder": "Material icon name (optional)",
                }
            ),
        }
