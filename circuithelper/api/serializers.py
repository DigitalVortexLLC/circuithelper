from rest_framework import serializers
from netbox.api.serializers import NetBoxModelSerializer
from circuits.api.serializers import CircuitSerializer
from ..models import (
    CircuitCost, CircuitContract, CircuitTicket,
    CircuitPath, ProviderAPIConfig
)


class CircuitCostSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:circuithelper-api:circuitcost-detail'
    )
    circuit = CircuitSerializer(nested=True)

    class Meta:
        model = CircuitCost
        fields = [
            'id', 'url', 'display', 'circuit', 'nrc', 'mrc',
            'currency', 'billing_account', 'last_updated_date',
            'created', 'last_updated', 'tags', 'custom_fields'
        ]


class CircuitContractSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:circuithelper-api:circuitcontract-detail'
    )
    circuit = CircuitSerializer(nested=True)

    class Meta:
        model = CircuitContract
        fields = [
            'id', 'url', 'display', 'circuit', 'contract_number',
            'start_date', 'end_date', 'term_months', 'auto_renew',
            'renewal_notice_days', 'early_termination_fee',
            'contract_file', 'notes', 'created', 'last_updated',
            'tags', 'custom_fields'
        ]


class CircuitTicketSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:circuithelper-api:circuitticket-detail'
    )
    circuit = CircuitSerializer(nested=True)

    class Meta:
        model = CircuitTicket
        fields = [
            'id', 'url', 'display', 'circuit', 'ticket_number',
            'subject', 'status', 'priority', 'opened_date',
            'closed_date', 'description', 'resolution',
            'external_url', 'created', 'last_updated',
            'tags', 'custom_fields'
        ]


class CircuitPathSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:circuithelper-api:circuitpath-detail'
    )
    circuit = CircuitSerializer(nested=True)

    class Meta:
        model = CircuitPath
        fields = [
            'id', 'url', 'display', 'circuit', 'kmz_file',
            'geojson_data', 'map_center_lat', 'map_center_lon',
            'map_zoom', 'path_distance_km', 'path_notes',
            'created', 'last_updated', 'tags', 'custom_fields'
        ]


class ProviderAPIConfigSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:circuithelper-api:providerapiconfig-detail'
    )

    class Meta:
        model = ProviderAPIConfig
        fields = [
            'id', 'url', 'display', 'provider', 'provider_type',
            'api_endpoint', 'api_key', 'sync_enabled',
            'sync_interval_hours', 'last_sync', 'sync_status',
            'created', 'last_updated', 'tags', 'custom_fields'
        ]
        # Don't expose api_secret in API responses
        extra_kwargs = {
            'api_secret': {'write_only': True}
        }
