from django.db import models

class Warehouse(models.Model):
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=255, blank=True)
    def __str__(self): return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=64, unique=True)
    reorder_point = models.PositiveIntegerField(default=10)
    def __str__(self): return f"{self.name} ({self.sku})"

class StockItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    class Meta:
        unique_together = ("product", "warehouse")
    def __str__(self): return f"{self.product} @ {self.warehouse}"
