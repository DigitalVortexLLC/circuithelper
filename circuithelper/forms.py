from circuits.models import Circuit
from django import forms
from netbox.forms import NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField

from .models import CircuitContract, CircuitCost, CircuitPath, CircuitTicket, ProviderAPIConfig


class CircuitCostForm(NetBoxModelForm):
    circuit = DynamicModelChoiceField(queryset=Circuit.objects.all(), label="Circuit")

    class Meta:
        model = CircuitCost
        fields = [
            "circuit",
            "nrc",
            "mrc",
            "currency",
            "billing_account",
            "last_updated_date",
            "tags",
        ]


class CircuitContractForm(NetBoxModelForm):
    circuit = DynamicModelChoiceField(queryset=Circuit.objects.all(), label="Circuit")

    class Meta:
        model = CircuitContract
        fields = [
            "circuit",
            "contract_number",
            "start_date",
            "end_date",
            "term_months",
            "auto_renew",
            "renewal_notice_days",
            "early_termination_fee",
            "contract_file",
            "notes",
            "tags",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class CircuitTicketForm(NetBoxModelForm):
    circuit = DynamicModelChoiceField(queryset=Circuit.objects.all(), label="Circuit")

    class Meta:
        model = CircuitTicket
        fields = [
            "circuit",
            "ticket_number",
            "subject",
            "status",
            "priority",
            "closed_date",
            "description",
            "resolution",
            "external_url",
            "tags",
        ]
        widgets = {
            "closed_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "resolution": forms.Textarea(attrs={"rows": 4}),
        }


class CircuitPathForm(NetBoxModelForm):
    circuit = DynamicModelChoiceField(queryset=Circuit.objects.all(), label="Circuit")

    class Meta:
        model = CircuitPath
        fields = [
            "circuit",
            "kmz_file",
            "map_center_lat",
            "map_center_lon",
            "map_zoom",
            "path_distance_km",
            "path_notes",
            "tags",
        ]
        widgets = {
            "path_notes": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "kmz_file": "Upload a KMZ file to visualize the circuit path on a map. The file will be automatically parsed.",
        }


class ProviderAPIConfigForm(NetBoxModelForm):
    class Meta:
        model = ProviderAPIConfig
        fields = [
            "provider",
            "provider_type",
            "api_endpoint",
            "api_key",
            "api_secret",
            "sync_enabled",
            "sync_interval_hours",
            "tags",
        ]
        widgets = {
            "api_secret": forms.PasswordInput(render_value=True),
        }
