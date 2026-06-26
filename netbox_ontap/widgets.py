from extras.dashboard.widgets import ObjectCountsWidget
from extras.dashboard.utils import register_widget
from django.utils.translation import gettext_lazy as _

@register_widget
class OntapObjectCountsWidget(ObjectCountsWidget):
    default_title = _('ONTAP Objects')
    description = _('Display the number of objects created for each ONTAP model.')
    
    default_config = {
        'models': [
            'netbox_ontap.svm',
            'netbox_ontap.volume',
            'netbox_ontap.qtree',
            'netbox_ontap.quota',
            'netbox_ontap.lun',
        ]
    }
