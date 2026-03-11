from netbox.plugins import PluginConfig

class NetBoxStorageConfig(PluginConfig):
    name = 'netbox_storage'
    verbose_name = ' NetBox ONTAP'
    description = 'Netbox ONTAP Storage Administration Plugin'
    version = '1.0.0'
    base_url = 'ontap'
    min_version = "4.3.0"
    author = 'Gabor Somogyvari'


config = NetBoxStorageConfig
