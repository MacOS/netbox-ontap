# SPDX-FileCopyrightText: 2026 Gabor Somogyvari, Leonhard Kreißig (Deutsche Telekom AG) <leonhard.kreissig@telekom.de>
#
# SPDX-License-Identifier: Apache-2.0

from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

cluster_item = PluginMenuItem(
    link="plugins:netbox_ontap:netappcluster_list",
    link_text="Clusters",
    permissions=["netbox_ontap.view_netappcluster"],
    buttons=[
        PluginMenuButton(
            link="plugins:netbox_ontap:netappcluster_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_ontap.add_netappcluster"],
        ),
        PluginMenuButton(
            link="plugins:netbox_ontap:netappcluster_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_ontap.add_netappcluster"],
        ),
    ],
)

node_item = PluginMenuItem(
    link="plugins:netbox_ontap:netappnode_list",
    link_text="Nodes",
    permissions=["netbox_ontap.view_netappnode"],
    buttons=[
        PluginMenuButton(
            link="plugins:netbox_ontap:netappnode_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_ontap.add_netappnode"],
        ),
        PluginMenuButton(
            link="plugins:netbox_ontap:netappnode_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_ontap.add_netappnode"],
        ),
    ],
)

aggregate_item = PluginMenuItem(
    link="plugins:netbox_ontap:netappaggregate_list",
    link_text="Aggregates",
    permissions=["netbox_ontap.view_netappaggregate"],
    buttons=[
        PluginMenuButton(
            link="plugins:netbox_ontap:netappaggregate_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_ontap.add_netappaggregate"],
        ),
        PluginMenuButton(
            link="plugins:netbox_ontap:netappaggregate_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_ontap.add_netappaggregate"],
        ),
    ],
)

svm_item = PluginMenuItem(
    link="plugins:netbox_ontap:netappsvm_list",
    link_text="SVMs",
    permissions=["netbox_ontap.view_netappsvm"],
    buttons=[
        PluginMenuButton(
            link="plugins:netbox_ontap:netappsvm_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_ontap.add_netappsvm"],
        ),
        PluginMenuButton(
            link="plugins:netbox_ontap:netappsvm_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_ontap.add_netappsvm"],
        ),
    ],
)

volume_item = PluginMenuItem(
    link="plugins:netbox_ontap:netappvolume_list",
    link_text="Volumes",
    permissions=["netbox_ontap.view_netappvolume"],
    buttons=[
        PluginMenuButton(
            link="plugins:netbox_ontap:netappvolume_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_ontap.add_netappvolume"],
        ),
        PluginMenuButton(
            link="plugins:netbox_ontap:netappvolume_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_ontap.add_netappvolume"],
        ),
    ],
)

qtree_item = PluginMenuItem(
    link="plugins:netbox_ontap:netappqtree_list",
    link_text="QTrees",
    permissions=["netbox_ontap.view_netappqtree"],
    buttons=[
        PluginMenuButton(
            link="plugins:netbox_ontap:netappqtree_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_ontap.add_netappqtree"],
        ),
        PluginMenuButton(
            link="plugins:netbox_ontap:netappqtree_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_ontap.add_netappqtree"],
        ),
    ],
)

quota_item = PluginMenuItem(
    link="plugins:netbox_ontap:netappquota_list",
    link_text="Quotas",
    permissions=["netbox_ontap.view_netappquota"],
    buttons=[
        PluginMenuButton(
            link="plugins:netbox_ontap:netappquota_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_ontap.add_netappquota"],
        ),
        PluginMenuButton(
            link="plugins:netbox_ontap:netappquota_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_ontap.add_netappquota"],
        ),
    ],
)

lun_item = PluginMenuItem(
    link="plugins:netbox_ontap:netapplun_list",
    link_text="LUNs",
    permissions=["netbox_ontap.view_netapplun"],
    buttons=[
        PluginMenuButton(
            link="plugins:netbox_ontap:netapplun_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_ontap.add_netapplun"],
        ),
        PluginMenuButton(
            link="plugins:netbox_ontap:netapplun_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_ontap.add_netapplun"],
        ),
    ],
)

menu = PluginMenu(
    label="Storage",
    groups=(
        ("Cluster", (cluster_item, node_item, aggregate_item)),
        ("Storage", (svm_item, volume_item, qtree_item, quota_item, lun_item)),
    ),
    icon_class="mdi mdi-nas",
)
