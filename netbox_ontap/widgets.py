from extras.dashboard.widgets import ObjectCountsWidget
from extras.dashboard.utils import register_widget
from django.utils.translation import gettext as _

@register_widget
class OntapObjectCountsWidget(ObjectCountsWidget):
    default_title = _('ONTAP Objects')
    description = _('Display the number of objects created for each ONTAP model.')
    
    default_config = {
        'models': [
            'netbox_ontap.netappcluster',
            'netbox_ontap.netappnode',
            'netbox_ontap.netappaggregate',
            'netbox_ontap.netappsvm',
            'netbox_ontap.netappvolume',
            'netbox_ontap.netappqtree',
            'netbox_ontap.netappquota',
            'netbox_ontap.netapplun',
        ]
    }
    
    def render(self, context):
        return super().render(context)
