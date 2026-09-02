from netbox.plugins import PluginConfig

class NetBoxOntapConfig(PluginConfig):
    name = 'netbox_ontap'
    verbose_name = ' NetBox ONTAP'
    description = 'Netbox ONTAP Storage Administration Plugin'
    version = '1.2.0'
    base_url = 'ontap'
    min_version = "4.3.0"
    author = 'Gabor Somogyvari, Leonhard Kreißig'

    def ready(self):
        super().ready()
        from . import widgets



config = NetBoxOntapConfig
