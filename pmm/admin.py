from django.contrib import admin
from .models import Maker, Brand, Scale, Tag, Kit, CreationStatus

admin.site.register(Maker)
admin.site.register(Brand)
admin.site.register(Scale)
admin.site.register(Tag)
admin.site.register(Kit)
admin.site.register(CreationStatus)
