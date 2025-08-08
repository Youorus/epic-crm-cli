from rest_framework import viewsets

from crm.contracts.models import Contract
from crm.contracts.permissions import ContractPermission
from crm.contracts.serializers import ContractSerializer


class ContractViewSet(viewsets.ModelViewSet):
    """
    ViewSet principal pour les contrats.
    - Gestion : peut tout faire.
    - Commercial et Support : lecture seule, accès limité à leurs clients/événements.
    """
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [ContractPermission]

    def get_queryset(self):
        user = self.request.user
        if user.role == "GESTION":
            return Contract.objects.all()
        if user.role == "COMMERCIAL":
            # Peut voir les contrats de ses clients
            return Contract.objects.filter(client__sales_contact=user)
        if user.role == "SUPPORT":
            return Contract.objects.all()
        return Contract.objects.none()