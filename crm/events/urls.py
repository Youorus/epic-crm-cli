from rest_framework.routers import DefaultRouter

from crm.events.views import EventViewSet

router = DefaultRouter()
router.register(r'', EventViewSet, basename='events')

urlpatterns = router.urls