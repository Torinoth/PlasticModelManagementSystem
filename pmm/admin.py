from django.contrib import admin
from pmm.models import PlasticModel, brand, scale, stock_history


class PlasticModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'scale', 'brand', 'stock', 'description')


class brandAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


class scaleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')


class stock_historyAdmin(admin.ModelAdmin):
    list_display = ('model', 'quantity_before', 'quantity_after', 'date')


admin.site.register(PlasticModel, PlasticModelAdmin)
admin.site.register(brand, brandAdmin)
admin.site.register(scale, scaleAdmin)
admin.site.register(stock_history, stock_historyAdmin)
