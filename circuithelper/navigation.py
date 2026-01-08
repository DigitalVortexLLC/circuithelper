from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

menu = PluginMenu(
    label="Circuit Manager",
    groups=(
        (
            "Financial",
            (
                PluginMenuItem(
                    link="plugins:circuithelper:circuitcost_list",
                    link_text="Circuit Costs",
                    buttons=(
                        PluginMenuButton(
                            link="plugins:circuithelper:circuitcost_add",
                            title="Add",
                            icon_class="mdi mdi-plus-thick",
                        ),
                    ),
                ),
            ),
        ),
        (
            "Contracts & Tickets",
            (
                PluginMenuItem(
                    link="plugins:circuithelper:circuitcontract_list",
                    link_text="Contracts",
                    buttons=(
                        PluginMenuButton(
                            link="plugins:circuithelper:circuitcontract_add",
                            title="Add",
                            icon_class="mdi mdi-plus-thick",
                        ),
                    ),
                ),
                PluginMenuItem(
                    link="plugins:circuithelper:circuitticket_list",
                    link_text="Tickets",
                    buttons=(
                        PluginMenuButton(
                            link="plugins:circuithelper:circuitticket_add",
                            title="Add",
                            icon_class="mdi mdi-plus-thick",
                        ),
                    ),
                ),
            ),
        ),
        (
            "Geographic",
            (
                PluginMenuItem(
                    link="plugins:circuithelper:circuitpath_list",
                    link_text="Circuit Paths",
                    buttons=(
                        PluginMenuButton(
                            link="plugins:circuithelper:circuitpath_add",
                            title="Add",
                            icon_class="mdi mdi-plus-thick",
                        ),
                    ),
                ),
            ),
        ),
        (
            "Integration",
            (
                PluginMenuItem(
                    link="plugins:circuithelper:providerapiconfig_list",
                    link_text="Provider API Configs",
                    buttons=(
                        PluginMenuButton(
                            link="plugins:circuithelper:providerapiconfig_add",
                            title="Add",
                            icon_class="mdi mdi-plus-thick",
                        ),
                    ),
                ),
            ),
        ),
    ),
    icon_class="mdi mdi-transit-connection-variant",
)
