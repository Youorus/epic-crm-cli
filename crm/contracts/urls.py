"""
Routes DRF pour l'API des contrats.

📌 Remarques :
- Ce router ne définit pas de préfixe explicite pour garder la flexibilité
  de l'inclusion dans le `urls.py` principal.
- Dans le fichier principal `urls.py` du projet, on pourra inclure ces routes ainsi :
      path('api/contracts/', include('crm.contracts.urls'))
- Cela permet de garder une structure d'URL claire et stable en production.
"""

from rest_framework.routers import DefaultRouter

from crm.contracts.views import ContractViewSet

# Nom d'application (utile pour le reverse URL dans Django)
app_name = "contracts"

# Création du router DRF pour gérer les endpoints REST automatiquement
router = DefaultRouter()

# Enregistrement du ViewSet des contrats :
# - Le préfixe vide "" permet d'ajouter directement les routes dans l'inclusion
# - basename='contracts' est utilisé pour générer les noms de routes
router.register(r'', ContractViewSet, basename='contracts')

# Liste finale des URL exposées par ce module
urlpatterns = router.urls