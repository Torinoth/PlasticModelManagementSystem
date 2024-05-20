from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet
from . import views

router = DefaultRouter()
router.register(r'products', ProductViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    # path('model/<int:model_id>/', views.model_detail, name='model_detail'),
]
