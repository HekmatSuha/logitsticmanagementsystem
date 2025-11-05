from django.db import models

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending","pending"),
        ("processing","processing"),
        ("delivered","delivered"),
        ("cancelled","cancelled"),
    ]
    customer_name = models.CharField(max_length=200)
    order_date = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    def __str__(self): return f"Order #{self.pk} - {self.customer_name}"
