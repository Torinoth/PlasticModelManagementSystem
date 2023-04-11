from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('model/<int:model_id>/', views.model_detail, name='model_detail'),
]
