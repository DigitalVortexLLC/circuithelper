from django.urls import path
from . import views

urlpatterns = [
    # CircuitCost URLs
    path('circuit-costs/', views.CircuitCostListView.as_view(), name='circuitcost_list'),
    path('circuit-costs/<int:pk>/', views.CircuitCostView.as_view(), name='circuitcost'),
    path('circuit-costs/add/', views.CircuitCostEditView.as_view(), name='circuitcost_add'),
    path('circuit-costs/<int:pk>/edit/', views.CircuitCostEditView.as_view(), name='circuitcost_edit'),
    path('circuit-costs/<int:pk>/delete/', views.CircuitCostDeleteView.as_view(), name='circuitcost_delete'),

    # CircuitContract URLs
    path('circuit-contracts/', views.CircuitContractListView.as_view(), name='circuitcontract_list'),
    path('circuit-contracts/<int:pk>/', views.CircuitContractView.as_view(), name='circuitcontract'),
    path('circuit-contracts/add/', views.CircuitContractEditView.as_view(), name='circuitcontract_add'),
    path('circuit-contracts/<int:pk>/edit/', views.CircuitContractEditView.as_view(), name='circuitcontract_edit'),
    path('circuit-contracts/<int:pk>/delete/', views.CircuitContractDeleteView.as_view(), name='circuitcontract_delete'),

    # CircuitTicket URLs
    path('circuit-tickets/', views.CircuitTicketListView.as_view(), name='circuitticket_list'),
    path('circuit-tickets/<int:pk>/', views.CircuitTicketView.as_view(), name='circuitticket'),
    path('circuit-tickets/add/', views.CircuitTicketEditView.as_view(), name='circuitticket_add'),
    path('circuit-tickets/<int:pk>/edit/', views.CircuitTicketEditView.as_view(), name='circuitticket_edit'),
    path('circuit-tickets/<int:pk>/delete/', views.CircuitTicketDeleteView.as_view(), name='circuitticket_delete'),

    # CircuitPath URLs
    path('circuit-paths/', views.CircuitPathListView.as_view(), name='circuitpath_list'),
    path('circuit-paths/<int:pk>/', views.CircuitPathView.as_view(), name='circuitpath'),
    path('circuit-paths/add/', views.CircuitPathEditView.as_view(), name='circuitpath_add'),
    path('circuit-paths/<int:pk>/edit/', views.CircuitPathEditView.as_view(), name='circuitpath_edit'),
    path('circuit-paths/<int:pk>/delete/', views.CircuitPathDeleteView.as_view(), name='circuitpath_delete'),

    # ProviderAPIConfig URLs
    path('provider-api-configs/', views.ProviderAPIConfigListView.as_view(), name='providerapiconfig_list'),
    path('provider-api-configs/<int:pk>/', views.ProviderAPIConfigView.as_view(), name='providerapiconfig'),
    path('provider-api-configs/add/', views.ProviderAPIConfigEditView.as_view(), name='providerapiconfig_add'),
    path('provider-api-configs/<int:pk>/edit/', views.ProviderAPIConfigEditView.as_view(), name='providerapiconfig_edit'),
    path('provider-api-configs/<int:pk>/delete/', views.ProviderAPIConfigDeleteView.as_view(), name='providerapiconfig_delete'),

    # Circuit detail enhancement
    path('circuits/<int:pk>/details/', views.circuit_detail_tab, name='circuit_detail_tab'),
]
