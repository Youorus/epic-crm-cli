from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API métier
    path('api/users/', include('crm.users.urls')),
    path('api/clients/', include('crm.clients.urls')),
    path('api/contracts/', include('crm.contracts.urls')),
    path('api/events/', include('crm.events.urls')),

    # Schéma OpenAPI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # --- Auth JWT (SimpleJWT) ---
    path('api/auth/jwt/create', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/jwt/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/jwt/verify', TokenVerifyView.as_view(), name='token_verify'),
    # UI Swagger & Redoc
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]