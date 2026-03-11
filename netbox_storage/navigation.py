from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

svm_item = PluginMenuItem(
    link="plugins:netbox_storage:svm_list",
    link_text="SVMs",
    permissions=["netbox_storage.view_svm"],
    buttons=[
        PluginMenuButton(
            link="plugins:netbox_storage:svm_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_storage.add_svm"],
        ),
        PluginMenuButton(
            link="plugins:netbox_storage:svm_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_storage.add_svm"],
        ),
    ],
)

volume_item = PluginMenuItem(
    link="plugins:netbox_storage:volume_list",
    link_text="Volumes",
    permissions=["netbox_storage.view_volume"],
    buttons=[
        PluginMenuButton(
            link="plugins:netbox_storage:volume_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_storage.add_volume"],
        ),
        PluginMenuButton(
            link="plugins:netbox_storage:volume_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_storage.add_volume"],
        ),
    ],
)

qtree_item = PluginMenuItem(
    link="plugins:netbox_storage:qtree_list",
    link_text="QTrees",
    permissions=["netbox_storage.view_qtree"],
    buttons=[
        PluginMenuButton(
            link="plugins:netbox_storage:qtree_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_storage.add_qtree"],
        ),
        PluginMenuButton(
            link="plugins:netbox_storage:qtree_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_storage.add_qtree"],
        ),
    ],
)

quota_item = PluginMenuItem(
    link="plugins:netbox_storage:quota_list",
    link_text="Quotas",
    permissions=["netbox_storage.view_quota"],
    buttons=[
        PluginMenuButton(
            link="plugins:netbox_storage:quota_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_storage.add_quota"],
        ),
        PluginMenuButton(
            link="plugins:netbox_storage:quota_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_storage.add_quota"],
        ),
    ],
)

lun_item = PluginMenuItem(
    link="plugins:netbox_storage:lun_list",
    link_text="LUNs",
    permissions=["netbox_storage.view_lun"],
    buttons=[
        PluginMenuButton(
            link="plugins:netbox_storage:lun_add",
            title="Add",
            icon_class="mdi mdi-plus-thick",
            permissions=["netbox_storage.add_lun"],
        ),
        PluginMenuButton(
            link="plugins:netbox_storage:lun_import",
            title="Import",
            icon_class="mdi mdi-upload",
            permissions=["netbox_storage.add_lun"],
        ),
    ],
)

menu = PluginMenu(
    label="Storage",
    groups=(("Storage", (svm_item, volume_item, qtree_item, quota_item, lun_item)),),
    icon_class="mdi mdi-nas",
)
