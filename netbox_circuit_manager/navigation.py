from netbox.plugins import PluginMenuButton, PluginMenuItem, PluginMenu

menu = PluginMenu(
    label='Circuit Manager',
    groups=(
        (
            'Financial',
            (
                PluginMenuItem(
                    link='plugins:netbox_circuit_manager:circuitcost_list',
                    link_text='Circuit Costs',
                    buttons=(
                        PluginMenuButton(
                            link='plugins:netbox_circuit_manager:circuitcost_add',
                            title='Add',
                            icon_class='mdi mdi-plus-thick',
                        ),
                    ),
                ),
            )
        ),
        (
            'Contracts & Tickets',
            (
                PluginMenuItem(
                    link='plugins:netbox_circuit_manager:circuitcontract_list',
                    link_text='Contracts',
                    buttons=(
                        PluginMenuButton(
                            link='plugins:netbox_circuit_manager:circuitcontract_add',
                            title='Add',
                            icon_class='mdi mdi-plus-thick',
                        ),
                    ),
                ),
                PluginMenuItem(
                    link='plugins:netbox_circuit_manager:circuitticket_list',
                    link_text='Tickets',
                    buttons=(
                        PluginMenuButton(
                            link='plugins:netbox_circuit_manager:circuitticket_add',
                            title='Add',
                            icon_class='mdi mdi-plus-thick',
                        ),
                    ),
                ),
            )
        ),
        (
            'Geographic',
            (
                PluginMenuItem(
                    link='plugins:netbox_circuit_manager:circuitpath_list',
                    link_text='Circuit Paths',
                    buttons=(
                        PluginMenuButton(
                            link='plugins:netbox_circuit_manager:circuitpath_add',
                            title='Add',
                            icon_class='mdi mdi-plus-thick',
                        ),
                    ),
                ),
            )
        ),
        (
            'Integration',
            (
                PluginMenuItem(
                    link='plugins:netbox_circuit_manager:providerapiconfig_list',
                    link_text='Provider API Configs',
                    buttons=(
                        PluginMenuButton(
                            link='plugins:netbox_circuit_manager:providerapiconfig_add',
                            title='Add',
                            icon_class='mdi mdi-plus-thick',
                        ),
                    ),
                ),
            )
        ),
    ),
    icon_class='mdi mdi-transit-connection-variant',
)
