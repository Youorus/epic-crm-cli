from rest_framework.routers import DefaultRouter

from crm.contracts.views import ContractViewSet

router = DefaultRouter()
router.register(r'', ContractViewSet, basename='contracts')

urlpatterns = router.urls