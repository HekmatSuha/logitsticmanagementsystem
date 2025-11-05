from django.db import models


class Shipment(models.Model):
    STATUS_CHOICES = [
        ("in_transit", "In Transit"),
        ("delayed", "Delayed"),
        ("on_time", "On Time"),
        ("issue", "Issue"),
        ("delivered", "Delivered"),
    ]
    PRIORITY_CHOICES = [
        ("high", "High"),
        ("medium", "Medium"),
        ("low", "Low"),
    ]

    tracking_id = models.CharField(max_length=40, unique=True)
    origin = models.CharField(max_length=120)
    destination = models.CharField(max_length=120)
    eta = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="in_transit")
    priority = models.CharField(max_length=12, choices=PRIORITY_CHOICES, default="medium")
    carrier = models.CharField(max_length=120, blank=True)
    contents = models.CharField(max_length=255, blank=True)
    driver_contact = models.CharField(max_length=120, blank=True)
    departure_time = models.DateTimeField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["eta", "tracking_id"]

    def __str__(self):
        return self.tracking_id

    @property
    def is_completed(self):
        return self.status == "delivered"


class ShipmentEvent(models.Model):
    shipment = models.ForeignKey(Shipment, related_name="events", on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    description = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True)
    icon = models.CharField(
        max_length=32,
        blank=True,
        help_text="Optional material icon name used to visually differentiate events.",
    )

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.shipment.tracking_id}: {self.description}"
