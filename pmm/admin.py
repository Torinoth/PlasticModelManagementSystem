from django.contrib import admin
from .models import Product


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'purchase_date', 'price', 'creation_status')


admin.site.register(Product, ProductAdmin)
