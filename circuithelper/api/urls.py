from netbox.api.routers import NetBoxRouter

from .views import (
    CircuitContractViewSet,
    CircuitCostViewSet,
    CircuitPathViewSet,
    CircuitTicketViewSet,
    ProviderAPIConfigViewSet,
)

router = NetBoxRouter()
router.register("circuit-costs", CircuitCostViewSet)
router.register("circuit-contracts", CircuitContractViewSet)
router.register("circuit-tickets", CircuitTicketViewSet)
router.register("circuit-paths", CircuitPathViewSet)
router.register("provider-api-configs", ProviderAPIConfigViewSet)

urlpatterns = router.urls
