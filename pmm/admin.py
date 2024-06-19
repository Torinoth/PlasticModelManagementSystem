from django.contrib import admin
from .models import *


# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('product_name', 'purchase_date', 'price', 'creation_status')


admin.site.register(Maker)
admin.site.register(Brand)
admin.site.register(Scale)
admin.site.register(Product)
admin.site.register(CreationStatus)
