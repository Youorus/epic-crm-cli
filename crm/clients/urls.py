"""
Routeur DRF pour l'API des Clients.

Bonnes pratiques :
- On n'enregistre pas de préfixe explicite ici afin que les routes soient relatives
  et puissent être montées proprement dans `urls.py` du projet.
- Dans `epic_crm/urls.py`, on inclut ce module ainsi :
      path('api/clients/', include('crm.clients.urls'))
  Cela permet de garder les chemins publics stables en production.
"""

from rest_framework.routers import DefaultRouter
from crm.clients.views import ClientViewSet

# Nom d'application pour la résolution de namespace dans Django
app_name = "clients"

# Création du routeur DRF
router = DefaultRouter()

# Enregistrement de la vue ClientViewSet sans préfixe (''), ce qui permet
# au point de montage `path('api/clients/', ...)` de définir le chemin complet.
router.register(r"", ClientViewSet, basename="clients")

# Liste finale des URL générées par le routeur
urlpatterns = router.urls