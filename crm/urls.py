from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    MeView,
    UserViewSet,
    CommercialClientViewSet,
    CommercialContractViewSet,
    CommercialEventViewSet,
    GlobalClientViewSet,
    GlobalContractViewSet,
    GlobalEventViewSet, GestionContractViewSet,
)

router = DefaultRouter()

# 🔐 Gestion des utilisateurs
router.register(r'users', UserViewSet, basename='user')

# 👁️ Lecture globale (tous les rôles)
router.register(r'clients', GlobalClientViewSet, basename='clients')
router.register(r'contracts', GlobalContractViewSet, basename='contracts')
router.register(r'events', GlobalEventViewSet, basename='events')

router.register(r'gestion/contracts', GestionContractViewSet, basename='gestion-contracts')

# 💼 Routes commerciales
router.register(r'commercial/clients', CommercialClientViewSet, basename='commercial-clients')
router.register(r'commercial/contracts', CommercialContractViewSet, basename='commercial-contracts')
router.register(r'commercial/events', CommercialEventViewSet, basename='commercial-events')

# Route perso
urlpatterns = [
    path('me/', MeView.as_view(), name='me'),
]

urlpatterns += router.urls