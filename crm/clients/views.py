from rest_framework import viewsets

from crm.clients.models import Client
from crm.clients.permissions import ClientPermission
from crm.clients.serializers import ClientSerializer


class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet principal pour les clients.
    Applique le principe du moindre privilège :
    - Commercial : CRUD sur ses clients, lecture tous les clients.
    - Gestion : tout accès.
    - Support : lecture seule.
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [ClientPermission]

    def get_queryset(self):
        user = self.request.user
        if user.role == "GESTION":
            return Client.objects.all()
        if user.role == "COMMERCIAL":
            # Peut voir tous les clients, mais ne peut éditer que les siens (géré par permission)
            return Client.objects.all()
        if user.role == "SUPPORT":
            # Lecture seule de tous les clients
            return Client.objects.all()
        return Client.objects.none()