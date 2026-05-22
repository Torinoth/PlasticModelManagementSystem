from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'kits', views.KitViewSet, basename='kit')
router.register(r'tags', views.TagViewSet, basename='tag')
router.register(r'makers', views.MakerViewSet, basename='maker')
router.register(r'brands', views.BrandViewSet, basename='brand')
router.register(r'scales', views.ScaleViewSet, basename='scale')
router.register(r'creation-statuses', views.CreationStatusViewSet, basename='creationstatus')

urlpatterns = [
    path('', include(router.urls)),
]
