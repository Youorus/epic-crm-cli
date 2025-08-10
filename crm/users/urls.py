"""
Configuration du routeur DRF pour l'API Utilisateurs.

⚙️ Fonctionnement :
- Ce fichier enregistre le `UserViewSet` dans un `DefaultRouter` DRF.
- Les routes générées permettent de gérer les opérations CRUD sur les utilisateurs.
- Ce routeur est inclus dans les URLs principales du projet via :
  path('api/users/', include('crm.users.urls'))

📌 Avantage :
- Génère automatiquement toutes les routes REST standard :
    GET /        → liste des utilisateurs
    POST /       → création d'un utilisateur
    GET /{id}/   → détails d'un utilisateur
    PUT /{id}/   → mise à jour complète
    PATCH /{id}/ → mise à jour partielle
    DELETE /{id}/→ suppression
"""

from rest_framework.routers import DefaultRouter
from crm.users.views import UserViewSet

# Création du routeur DRF
router = DefaultRouter()

# Enregistre le ViewSet des utilisateurs
router.register(r'', UserViewSet, basename='users')

# Exporte les URLs générées automatiquement par le routeur
urlpatterns = router.urls