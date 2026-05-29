from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from pmm.views import (
    csrf_view, login_view, logout_view, me_view,
    register_view, verify_email_view, users_view, approve_user_view,
    suspend_user_view, delete_user_view,
    user_kits_view, user_summary_view,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('pmm.urls')),
    path('api/auth/csrf/', csrf_view),
    path('api/auth/login/', login_view),
    path('api/auth/logout/', logout_view),
    path('api/auth/me/', me_view),
    path('api/auth/register/', register_view),
    path('api/auth/verify-email/', verify_email_view),
    path('api/auth/users/', users_view),
    path('api/auth/users/<int:user_id>/approve/', approve_user_view),
    path('api/auth/users/<int:user_id>/suspend/', suspend_user_view),
    path('api/auth/users/<int:user_id>/', delete_user_view),
    path('api/u/<str:username>/summary/', user_summary_view),
    path('api/u/<str:username>/', user_kits_view),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
