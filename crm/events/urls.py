"""
Routes DRF pour l’API des événements (`Event`).

⚙️ Bonnes pratiques :
- On ne définit pas de préfixe explicite ici, afin de pouvoir monter ce routeur
  sous un chemin défini au niveau du projet (ex. `path("api/events/", include(...))`).
- Cela permet de garder les URL publiques stables en production, tout en isolant
  la configuration par module.
"""

from rest_framework.routers import DefaultRouter

from crm.events.views import EventViewSet

# Nom d’espace de l’application (utile pour le reverse des URLs)
app_name = "events"

# Création du routeur et enregistrement du ViewSet principal
router = DefaultRouter()
router.register(r"", EventViewSet, basename="events")

# Exposition des URL générées automatiquement par DRF
urlpatterns = router.urls