from netbox.plugins import PluginConfig

class NetBoxOntapConfig(PluginConfig):
    name = 'netbox_ontap'
    verbose_name = ' NetBox ONTAP'
    description = 'Netbox ONTAP Storage Administration Plugin'
    version = '1.1.0'
    base_url = 'ontap'
    min_version = "4.3.0"
    author = 'Gabor Somogyvari, Leonhard Kreißig'


config = NetBoxOntapConfig
