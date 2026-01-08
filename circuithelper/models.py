from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from circuits.models import Circuit


class CircuitCost(NetBoxModel):
    """
    Track NRC and MRC costs for circuits
    """

    circuit = models.OneToOneField(to=Circuit, on_delete=models.CASCADE, related_name="costs")
    nrc = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Non-Recurring Charge",
        help_text="One-time installation or setup charge",
        validators=[MinValueValidator(0)],
    )
    mrc = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Monthly Recurring Charge",
        help_text="Monthly service charge",
        validators=[MinValueValidator(0)],
    )
    currency = models.CharField(
        max_length=3, default="USD", help_text="ISO 4217 currency code (e.g., USD, EUR, GBP)"
    )
    billing_account = models.CharField(
        max_length=100, blank=True, help_text="Provider billing account number"
    )
    last_updated_date = models.DateField(
        null=True, blank=True, help_text="Date when cost information was last updated"
    )

    class Meta:
        ordering = ["circuit"]
        verbose_name = "Circuit Cost"
        verbose_name_plural = "Circuit Costs"

    def __str__(self):
        return f"{self.circuit} - MRC: {self.mrc} {self.currency}"

    def get_absolute_url(self):
        return reverse("plugins:circuithelper:circuitcost", args=[self.pk])


class CircuitContract(NetBoxModel):
    """
    Store contract terms and documents for circuits
    """

    circuit = models.ForeignKey(to=Circuit, on_delete=models.CASCADE, related_name="contracts")
    contract_number = models.CharField(max_length=100, help_text="Contract or agreement number")
    start_date = models.DateField(help_text="Contract start date")
    end_date = models.DateField(null=True, blank=True, help_text="Contract end date")
    term_months = models.PositiveIntegerField(
        null=True, blank=True, help_text="Contract term in months"
    )
    auto_renew = models.BooleanField(default=False, help_text="Does the contract auto-renew?")
    renewal_notice_days = models.PositiveIntegerField(
        null=True, blank=True, help_text="Days notice required for non-renewal"
    )
    early_termination_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Fee for early contract termination",
    )
    contract_file = models.FileField(
        upload_to="circuit_contracts/%Y/%m/",
        null=True,
        blank=True,
        help_text="Upload contract PDF or document",
    )
    notes = models.TextField(blank=True, help_text="Additional contract notes")

    class Meta:
        ordering = ["circuit", "-start_date"]
        verbose_name = "Circuit Contract"
        verbose_name_plural = "Circuit Contracts"

    def __str__(self):
        return f"{self.circuit} - {self.contract_number}"

    def get_absolute_url(self):
        return reverse("plugins:circuithelper:circuitcontract", args=[self.pk])


class CircuitTicket(NetBoxModel):
    """
    Track support tickets related to circuits
    """

    TICKET_STATUS_CHOICES = (
        ("open", "Open"),
        ("in_progress", "In Progress"),
        ("pending", "Pending"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    )

    TICKET_PRIORITY_CHOICES = (
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("critical", "Critical"),
    )

    circuit = models.ForeignKey(to=Circuit, on_delete=models.CASCADE, related_name="tickets")
    ticket_number = models.CharField(
        max_length=100, unique=True, help_text="Provider ticket number"
    )
    subject = models.CharField(max_length=255, help_text="Ticket subject or title")
    status = models.CharField(max_length=20, choices=TICKET_STATUS_CHOICES, default="open")
    priority = models.CharField(max_length=20, choices=TICKET_PRIORITY_CHOICES, default="medium")
    opened_date = models.DateTimeField(auto_now_add=True, help_text="Date ticket was opened")
    closed_date = models.DateTimeField(null=True, blank=True, help_text="Date ticket was closed")
    description = models.TextField(help_text="Detailed description of the issue")
    resolution = models.TextField(blank=True, help_text="Resolution details")
    external_url = models.URLField(blank=True, help_text="Link to external ticketing system")

    class Meta:
        ordering = ["-opened_date"]
        verbose_name = "Circuit Ticket"
        verbose_name_plural = "Circuit Tickets"

    def __str__(self):
        return f"{self.ticket_number} - {self.circuit}"

    def get_absolute_url(self):
        return reverse("plugins:circuithelper:circuitticket", args=[self.pk])


class CircuitPath(NetBoxModel):
    """
    Store geographic path information for circuits
    """

    circuit = models.OneToOneField(to=Circuit, on_delete=models.CASCADE, related_name="path")
    kmz_file = models.FileField(
        upload_to="circuit_paths/%Y/%m/",
        null=True,
        blank=True,
        help_text="Upload KMZ file showing circuit path",
    )
    geojson_data = models.JSONField(null=True, blank=True, help_text="Parsed GeoJSON data from KMZ")
    map_center_lat = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True, help_text="Map center latitude"
    )
    map_center_lon = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True, help_text="Map center longitude"
    )
    map_zoom = models.PositiveIntegerField(default=10, help_text="Default map zoom level")
    path_distance_km = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Total path distance in kilometers",
    )
    path_notes = models.TextField(blank=True, help_text="Notes about the circuit path")

    class Meta:
        ordering = ["circuit"]
        verbose_name = "Circuit Path"
        verbose_name_plural = "Circuit Paths"

    def __str__(self):
        return f"{self.circuit} - Path"

    def get_absolute_url(self):
        return reverse("plugins:circuithelper:circuitpath", args=[self.pk])


class ProviderAPIConfig(NetBoxModel):
    """
    Configuration for provider API integrations
    """

    PROVIDER_CHOICES = (
        ("lumen", "Lumen"),
        ("att", "AT&T"),
        ("verizon", "Verizon"),
        ("zayo", "Zayo"),
        ("custom", "Custom"),
    )

    provider = models.ForeignKey(
        to="circuits.Provider", on_delete=models.CASCADE, related_name="api_configs"
    )
    provider_type = models.CharField(
        max_length=50, choices=PROVIDER_CHOICES, help_text="Provider API type"
    )
    api_endpoint = models.URLField(help_text="API base URL")
    api_key = models.CharField(max_length=255, blank=True, help_text="API authentication key")
    api_secret = models.CharField(
        max_length=255, blank=True, help_text="API secret (stored encrypted)"
    )
    sync_enabled = models.BooleanField(default=False, help_text="Enable automatic synchronization")
    sync_interval_hours = models.PositiveIntegerField(
        default=24, help_text="Hours between automatic syncs"
    )
    last_sync = models.DateTimeField(
        null=True, blank=True, help_text="Last successful sync timestamp"
    )
    sync_status = models.CharField(max_length=100, blank=True, help_text="Last sync status message")

    class Meta:
        ordering = ["provider"]
        verbose_name = "Provider API Configuration"
        verbose_name_plural = "Provider API Configurations"
        unique_together = ["provider", "provider_type"]

    def __str__(self):
        return f"{self.provider} - {self.provider_type}"

    def get_absolute_url(self):
        return reverse("plugins:circuithelper:providerapiconfig", args=[self.pk])
