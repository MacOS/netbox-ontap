import django_tables2 as tables

from django.template.defaultfilters import filesizeformat
from netbox.tables import NetBoxTable
from django.db.models.functions import Coalesce, Concat
from django.db.models import Value

from .models import (
    NetAppAggregate,
    NetAppCluster,
    NetAppLUN,
    NetAppNode,
    NetAppQTree,
    NetAppQuota,
    NetAppSVM,
    NetAppVolume,
)


class ClusterTable(NetBoxTable):
    name = tables.Column(linkify=True)
    management_ip = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = NetAppCluster
        fields = ("pk", "id", "name", "management_ip", "ontap_version", "uuid", "description", "actions")
        default_columns = ("name", "management_ip", "ontap_version")


class NodeTable(NetBoxTable):
    name = tables.Column(linkify=True)
    cluster = tables.Column(linkify=True)
    device = tables.Column(linkify=True)
    management_ip = tables.Column(linkify=True)
    class Meta(NetBoxTable.Meta):
        model = NetAppNode
        fields = (
            "pk",
            "id",
            "name",
            "cluster",
            "device",
            "model",
            "serial_number",
            "management_ip",
            "uuid",
            "description",
            "actions",
        )
        default_columns = ("name", "cluster", "device", "model")


class AggregateTable(NetBoxTable):
    name = tables.Column(linkify=True)
    node = tables.Column(linkify=True)
    cluster = tables.Column(linkify=True, order_by='node__cluster__name')

    class Meta(NetBoxTable.Meta):
        model = NetAppAggregate
        fields = ("pk", "id", "name", "node", "cluster", "size", "uuid", "description", "actions")
        default_columns = ("name", "node", "cluster", "size")

    def render_size(self, value):
        if value in (None, 0):
            return "—"
        return filesizeformat(value)


class SVMTable(NetBoxTable):
    name = tables.Column(linkify=True)
    cluster = tables.Column(linkify=True)
    tenant = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = NetAppSVM
        fields = ("pk", "id", "name", "cluster", "tenant", "uuid", "description", "actions")
        default_columns = ("name", "cluster", "tenant")


class VolumeTable(NetBoxTable):
    name = tables.Column(linkify=True)
    svm = tables.Column(linkify=True)
    aggregate = tables.Column(linkify=True)
    tenant = tables.Column(accessor='get_tenant', linkify=True, order_by='_tenant_sort')

    class Meta(NetBoxTable.Meta):
        model = NetAppVolume
        fields = ("pk", "id", "name", "svm", "aggregate", "size", "tenant", "uuid", "description", "actions")
        default_columns = ("name", "svm", "aggregate", "size", "tenant")

    def order_tenant(self, queryset, is_descending):
        queryset = queryset.annotate(
            _tenant_sort=Coalesce('tenant__name', 'svm__tenant__name')
        )
        modifier = '-' if is_descending else ''
        return (queryset.order_by(f"{modifier}_tenant_sort"), True)

    def render_size(self, value):
        if value in (None, 0):
            return "—"
        return filesizeformat(value)


class QTreeTable(NetBoxTable):
    name = tables.Column(linkify=True)
    volume = tables.Column(linkify=True)
    svm = tables.Column(linkify=True, order_by='volume__svm__name')

    class Meta(NetBoxTable.Meta):
        model = NetAppQTree
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
        model = NetAppQuota
        fields = (
            "pk",
            "id",
            "display_name",
            "volume",
            "qtree",
            "space_hard_limit",
            "space_soft_limit",
            "files_hard_limit",
            "files_soft_limit",
            "index",
            "description",
            "svm",
            "tenant",
            "actions",
        )
        default_columns = ("display_name", "tenant", "qtree", "index", "space_hard_limit")

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

    def render_space_hard_limit(self, value):
        if value is None:
            return "Metering quota"
        return filesizeformat(value)

    def render_space_soft_limit(self, value):
        if value is None:
            return "—"
        return filesizeformat(value)


class LUNTable(NetBoxTable):
    name = tables.Column(linkify=True)
    tenant = tables.Column(accessor='get_tenant', linkify=True, order_by='_tenant_sort')
    volume = tables.Column(linkify=True)
    qtree = tables.Column(linkify=True)

    class Meta(NetBoxTable.Meta):
        model = NetAppLUN
        fields = (
            "pk",
            "id",
            "name",
            "tenant",
            "volume",
            "qtree",
            "size",
            "os_type",
            "wwn",
            "uuid",
            "description", 
            "svm",
            "actions",
        )
        default_columns = ("name", "tenant", "volume", "qtree", "size", "os_type")

    def order_tenant(self, queryset, is_descending):
        queryset = queryset.annotate(
            _tenant_sort=Coalesce('tenant__name', 'volume__tenant__name', 'volume__svm__tenant__name')
        )
        modifier = '-' if is_descending else ''
        return (queryset.order_by(f"{modifier}_tenant_sort"), True)

    def render_size(self, value):
        return filesizeformat(value)
