from django.contrib import admin
from django.urls import path, include
from pmm.views import csrf_view, login_view, logout_view, me_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('pmm.urls')),
    path('api/auth/csrf/', csrf_view),
    path('api/auth/login/', login_view),
    path('api/auth/logout/', logout_view),
    path('api/auth/me/', me_view),
]
