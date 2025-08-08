from rest_framework.routers import DefaultRouter

from crm.users.views import UserViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='users')

urlpatterns = router.urls