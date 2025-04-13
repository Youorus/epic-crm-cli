from django.urls import path
from .views import MeView, UserViewSet, CommercialClientViewSet, CommercialContractViewSet, \
    CommercialEventViewSet  # + autres importations
from rest_framework.routers import DefaultRouter

# routes automatiques
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'clients', CommercialClientViewSet, basename='clients')
router.register(r'commercial/clients', CommercialClientViewSet, basename='commercial-clients')
router.register(r'commercial/contracts', CommercialContractViewSet, basename='commercial-contracts')
router.register(r'commercial/events', CommercialEventViewSet, basename='commercial-events')

# URL patterns combinées
urlpatterns = [
    path('me/', MeView.as_view(), name='me'),
]

urlpatterns += router.urls