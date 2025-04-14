from rest_framework import viewsets, filters
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, Client, Contract, Event
from .permission import IsGestionOnly, IsCommercial, IsSupport
from .serializers import UserSerializer, ClientSerializer, ContractSerializer, EventSerializer

# --- Gestion des utilisateurs (seulement pour l'équipe de gestion) ---
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsGestionOnly]

# --- Lecture globale : accessible à tous les utilisateurs connectés ---
class GlobalClientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

class GlobalContractViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer
    permission_classes = [IsAuthenticated]

class GlobalEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

# --- Commercial : client, contrat, événement liés à leurs propres clients ---
class CommercialClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    permission_classes = [IsCommercial]

    def get_queryset(self):
        return Client.objects.all()

    def perform_create(self, serializer):
        serializer.save(sales_contact=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.sales_contact != self.request.user:
            raise PermissionDenied("Vous ne pouvez modifier que vos propres clients.")
        serializer.save()

class CommercialContractViewSet(viewsets.ModelViewSet):
    serializer_class = ContractSerializer
    permission_classes = [IsCommercial]
    filter_backends = [filters.SearchFilter]
    search_fields = ['is_signed', 'amount_due']

    def get_queryset(self):
        return Contract.objects.filter(sales_contact=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.sales_contact != self.request.user:
            raise PermissionDenied("Vous ne pouvez modifier que vos propres contrats.")
        serializer.save()

class CommercialEventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsCommercial]

    def get_queryset(self):
        return Event.objects.filter(contract__sales_contact=self.request.user)

    def perform_create(self, serializer):
        contract = serializer.validated_data.get("contract")
        if contract.sales_contact != self.request.user:
            raise PermissionDenied("Vous ne pouvez créer des événements que pour vos contrats.")
        serializer.save()

# --- Support : ne peut modifier que les événements qui leur sont assignés ---
class SupportEventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsSupport]

    def get_queryset(self):
        return Event.objects.filter(support_contact=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.support_contact != self.request.user:
            raise PermissionDenied("Vous ne pouvez modifier que les événements qui vous sont assignés.")
        serializer.save()

# --- MeView (récupération du profil utilisateur connecté) ---
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
        })
