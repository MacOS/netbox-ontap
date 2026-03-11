from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

svm_item = PluginMenuItem(
    link="plugins:netbox_ontap:svm_list",
    link_text="SVMs",
    permissions=["netbox_ontap.view_svm"],
    buttons=[
        PluginMenuButton(
            link="plugins:netbox_ontap:svm_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_ontap.add_svm"],
        ),
        PluginMenuButton(
            link="plugins:netbox_ontap:svm_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_ontap.add_svm"],
        ),
    ],
)

volume_item = PluginMenuItem(
    link="plugins:netbox_ontap:volume_list",
    link_text="Volumes",
    permissions=["netbox_ontap.view_volume"],
    buttons=[
        PluginMenuButton(
            link="plugins:netbox_ontap:volume_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_ontap.add_volume"],
        ),
        PluginMenuButton(
            link="plugins:netbox_ontap:volume_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_ontap.add_volume"],
        ),
    ],
)

qtree_item = PluginMenuItem(
    link="plugins:netbox_ontap:qtree_list",
    link_text="QTrees",
    permissions=["netbox_ontap.view_qtree"],
    buttons=[
        PluginMenuButton(
            link="plugins:netbox_ontap:qtree_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_ontap.add_qtree"],
        ),
        PluginMenuButton(
            link="plugins:netbox_ontap:qtree_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_ontap.add_qtree"],
        ),
    ],
)

quota_item = PluginMenuItem(
    link="plugins:netbox_ontap:quota_list",
    link_text="Quotas",
    permissions=["netbox_ontap.view_quota"],
    buttons=[
        PluginMenuButton(
            link="plugins:netbox_ontap:quota_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_ontap.add_quota"],
        ),
        PluginMenuButton(
            link="plugins:netbox_ontap:quota_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_ontap.add_quota"],
        ),
    ],
)

lun_item = PluginMenuItem(
    link="plugins:netbox_ontap:lun_list",
    link_text="LUNs",
    permissions=["netbox_ontap.view_lun"],
    buttons=[
        PluginMenuButton(
            link="plugins:netbox_ontap:lun_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_ontap.add_lun"],
        ),
        PluginMenuButton(
            link="plugins:netbox_ontap:lun_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_ontap.add_lun"],
        ),
    ],
)

menu = PluginMenu(
    label="Storage",
    groups=(("Storage", (svm_item, volume_item, qtree_item, quota_item, lun_item)),),
    icon_class="mdi mdi-nas",
)
