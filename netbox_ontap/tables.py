import django_tables2 as tables

from django.template.defaultfilters import filesizeformat
from netbox.tables import NetBoxTable

from .models import LUN, QTree, Quota, SVM, Volume


class SVMTable(NetBoxTable):
    name = tables.Column(linkify=True)
    cluster = tables.Column(linkify=True)
    tenant = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = SVM
        fields = ("pk", "id", "name", "cluster", "tenant", "uuid", "description", "actions")
        default_columns = ("name", "cluster", "tenant")


class VolumeTable(NetBoxTable):
    name = tables.Column(linkify=True)
    svm = tables.Column(linkify=True)
    tenant = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = Volume
        fields = ("pk", "id", "name", "svm", "tenant", "uuid", "description", "actions")
        default_columns = ("name", "svm", "tenant")


class QTreeTable(NetBoxTable):
    name = tables.Column(linkify=True)
    volume = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = QTree
        fields = ("pk", "id", "name", "volume", "uuid", "description", "actions")
        default_columns = ("name", "volume")


class QuotaTable(NetBoxTable):
    display_name = tables.Column(verbose_name="Name", linkify=True)
    qtree = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = Quota
        fields = ("pk", "id", "display_name", "qtree", "size", "index", "description", "actions")
        default_columns = ("display_name", "qtree", "size")

    def render_size(self, value):
        if value in (None, 0):
            return "Metering quota"
        return filesizeformat(value)


class LUNTable(NetBoxTable):
    name = tables.Column(linkify=True)
    tenant = tables.Column(linkify=True)
    volume = tables.Column(linkify=True)
    qtree = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = LUN
        fields = (
            "pk",
            "id",
            "name",
            "tenant",
            "volume",
            "qtree",
            "size",
            "wwn",
            "uuid",
            "description",
            "actions",
        )
        default_columns = ("name", "tenant", "volume", "qtree", "size")

    def render_size(self, value):
        return filesizeformat(value)
