from circuits.models import Circuit
from django.shortcuts import get_object_or_404, render
from netbox.views import generic

from .forms import (
    CircuitContractForm,
    CircuitCostForm,
    CircuitPathForm,
    CircuitTicketForm,
    ProviderAPIConfigForm,
)
from .models import CircuitContract, CircuitCost, CircuitPath, CircuitTicket, ProviderAPIConfig
from .utils import calculate_path_distance, generate_folium_map, parse_kmz_file


# CircuitCost Views
class CircuitCostListView(generic.ObjectListView):
    queryset = CircuitCost.objects.all()
    filterset = None
    table = None


class CircuitCostView(generic.ObjectView):
    queryset = CircuitCost.objects.all()


class CircuitCostEditView(generic.ObjectEditView):
    queryset = CircuitCost.objects.all()
    form = CircuitCostForm


class CircuitCostDeleteView(generic.ObjectDeleteView):
    queryset = CircuitCost.objects.all()


# CircuitContract Views
class CircuitContractListView(generic.ObjectListView):
    queryset = CircuitContract.objects.all()
    filterset = None
    table = None


class CircuitContractView(generic.ObjectView):
    queryset = CircuitContract.objects.all()


class CircuitContractEditView(generic.ObjectEditView):
    queryset = CircuitContract.objects.all()
    form = CircuitContractForm


class CircuitContractDeleteView(generic.ObjectDeleteView):
    queryset = CircuitContract.objects.all()


# CircuitTicket Views
class CircuitTicketListView(generic.ObjectListView):
    queryset = CircuitTicket.objects.all()
    filterset = None
    table = None


class CircuitTicketView(generic.ObjectView):
    queryset = CircuitTicket.objects.all()


class CircuitTicketEditView(generic.ObjectEditView):
    queryset = CircuitTicket.objects.all()
    form = CircuitTicketForm


class CircuitTicketDeleteView(generic.ObjectDeleteView):
    queryset = CircuitTicket.objects.all()


# CircuitPath Views
class CircuitPathListView(generic.ObjectListView):
    queryset = CircuitPath.objects.all()
    filterset = None
    table = None


class CircuitPathView(generic.ObjectView):
    queryset = CircuitPath.objects.all()

    def get_extra_context(self, request, instance):
        context = super().get_extra_context(request, instance)

        # Generate interactive map if geojson data exists
        if instance.geojson_data and instance.map_center_lat and instance.map_center_lon:
            center = (float(instance.map_center_lat), float(instance.map_center_lon))
            context["map_html"] = generate_folium_map(
                instance.geojson_data, center, instance.map_zoom
            )
        else:
            context["map_html"] = None

        return context


class CircuitPathEditView(generic.ObjectEditView):
    queryset = CircuitPath.objects.all()
    form = CircuitPathForm

    def post(self, request, *args, **kwargs):
        obj = self.alter_object(self.get_object(kwargs), request, args, kwargs)
        form = self.form(data=request.POST, files=request.FILES, instance=obj)

        if form.is_valid():
            # Process KMZ file if uploaded
            if "kmz_file" in request.FILES:
                kmz_file = request.FILES["kmz_file"]
                geojson_data, center_coords = parse_kmz_file(kmz_file)

                if geojson_data and center_coords:
                    form.instance.geojson_data = geojson_data
                    form.instance.map_center_lat = center_coords[0]
                    form.instance.map_center_lon = center_coords[1]

                    # Calculate path distance
                    distance = calculate_path_distance(geojson_data)
                    if distance:
                        form.instance.path_distance_km = distance

            return self.form_valid(form)

        return self.form_invalid(form)


class CircuitPathDeleteView(generic.ObjectDeleteView):
    queryset = CircuitPath.objects.all()


# ProviderAPIConfig Views
class ProviderAPIConfigListView(generic.ObjectListView):
    queryset = ProviderAPIConfig.objects.all()
    filterset = None
    table = None


class ProviderAPIConfigView(generic.ObjectView):
    queryset = ProviderAPIConfig.objects.all()


class ProviderAPIConfigEditView(generic.ObjectEditView):
    queryset = ProviderAPIConfig.objects.all()
    form = ProviderAPIConfigForm


class ProviderAPIConfigDeleteView(generic.ObjectDeleteView):
    queryset = ProviderAPIConfig.objects.all()


# Circuit Enhancement View - Shows all extended data for a circuit
def circuit_detail_tab(request, pk):
    """
    Custom view to display circuit extensions in a tabbed interface.
    """
    circuit = get_object_or_404(Circuit, pk=pk)

    # Get related data
    try:
        costs = circuit.costs
    except CircuitCost.DoesNotExist:
        costs = None

    contracts = circuit.contracts.all()
    tickets = circuit.tickets.all()

    try:
        path = circuit.path
        map_html = None
        if path.geojson_data and path.map_center_lat and path.map_center_lon:
            center = (float(path.map_center_lat), float(path.map_center_lon))
            map_html = generate_folium_map(path.geojson_data, center, path.map_zoom)
    except CircuitPath.DoesNotExist:
        path = None
        map_html = None

    context = {
        "circuit": circuit,
        "costs": costs,
        "contracts": contracts,
        "tickets": tickets,
        "path": path,
        "map_html": map_html,
    }

    return render(request, "circuithelper/circuit_detail_tab.html", context)
