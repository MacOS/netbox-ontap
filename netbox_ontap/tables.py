import django_tables2 as tables

from django.template.defaultfilters import filesizeformat
from netbox.tables import NetBoxTable
from django.db.models.functions import Coalesce, Concat
from django.db.models import Value

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
    svm = tables.Column(linkify=True, order_by='volume__svm__name')

    class Meta(NetBoxTable.Meta):
        model = QTree
        fields = ("pk", "id", "name", "volume", "description", "svm", "tenant", "actions")
        default_columns = ("name", "volume", "svm", "tenant")

    def order_tenant(self, queryset, is_descending):
        queryset = queryset.annotate(
            _tenant_sort=Coalesce('volume__tenant__name', 'volume__svm__tenant__name')
        )
        modifier = '-' if is_descending else ''
        return (queryset.order_by(f"{modifier}_tenant_sort"), True)


class QuotaTable(NetBoxTable):
    display_name = tables.Column(verbose_name="Name", linkify=True)
    volume = tables.Column(linkify=True)
    qtree = tables.Column(linkify=True)

    svm = tables.Column(linkify=True, order_by='volume__svm__name')
    tenant = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = Quota
        fields = ("pk", "id", "display_name", "volume", "qtree", "size", "index", "description", "svm", "tenant", "actions")
        default_columns = ("display_name", "tenant", "qtree", "index", "size")

    def order_display_name(self, queryset, is_descending):
        queryset = queryset.annotate(
            _display_name_sort=Concat(
                'volume__name',
                Value(' - '),
                Coalesce('qtree__name', Value('0'))
            )
        )
        modifier = '-' if is_descending else ''
        return (queryset.order_by(f"{modifier}_display_name_sort"), True)

    def order_tenant(self, queryset, is_descending):
        queryset = queryset.annotate(
            _tenant_sort=Coalesce('volume__tenant__name', 'volume__svm__tenant__name')
        )
        modifier = '-' if is_descending else ''
        return (queryset.order_by(f"{modifier}_tenant_sort"), True)

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
            "svm",
            "actions",
        )
        default_columns = ("name", "tenant", "volume", "qtree", "size")

    def render_size(self, value):
        return filesizeformat(value)
