from rest_framework import viewsets

from crm.events.models import Event
from crm.events.permissions import EventPermission
from crm.events.serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet principal pour les événements.
    - Gestion : tout accès.
    - Commercial : accès aux événements de ses clients.
    - Support : accès lecture/édition uniquement à ses événements assignés.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [EventPermission]

    def get_queryset(self):
        user = self.request.user
        if user.role == "GESTION":
            return Event.objects.all()
        if user.role == "COMMERCIAL":
            # Accès aux événements liés à ses clients
            return Event.objects.filter(client__sales_contact=user)
        if user.role == "SUPPORT":
            # Accès uniquement aux événements qui lui sont assignés
            return Event.objects.filter(support_contact=user)
        return Event.objects.none()