from netbox.api.viewsets import NetBoxModelViewSet

from ..models import CircuitContract, CircuitCost, CircuitPath, CircuitTicket, ProviderAPIConfig
from .serializers import (
    CircuitContractSerializer,
    CircuitCostSerializer,
    CircuitPathSerializer,
    CircuitTicketSerializer,
    ProviderAPIConfigSerializer,
)


class CircuitCostViewSet(NetBoxModelViewSet):
    queryset = CircuitCost.objects.all()
    serializer_class = CircuitCostSerializer


class CircuitContractViewSet(NetBoxModelViewSet):
    queryset = CircuitContract.objects.all()
    serializer_class = CircuitContractSerializer


class CircuitTicketViewSet(NetBoxModelViewSet):
    queryset = CircuitTicket.objects.all()
    serializer_class = CircuitTicketSerializer


class CircuitPathViewSet(NetBoxModelViewSet):
    queryset = CircuitPath.objects.all()
    serializer_class = CircuitPathSerializer


class ProviderAPIConfigViewSet(NetBoxModelViewSet):
    queryset = ProviderAPIConfig.objects.all()
    serializer_class = ProviderAPIConfigSerializer
