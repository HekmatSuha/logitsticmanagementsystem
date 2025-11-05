from django.contrib import admin
from .models import Warehouse, Product, StockItem
admin.site.register(Warehouse)
admin.site.register(Product)
admin.site.register(StockItem)
