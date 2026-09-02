from netbox.filtersets import NetBoxModelFilterSet
from django.db.models import Q
import django_filters

from tenancy.models import Tenant

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


class ClusterFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = NetAppCluster
        fields = ("id", "name", "uuid")

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(uuid__icontains=value)
        )


class NodeFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = NetAppNode
        fields = ("id", "name", "cluster", "device", "uuid")

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(uuid__icontains=value)
            | Q(serial_number__icontains=value)
            | Q(cluster__name__icontains=value)
        )


class AggregateFilterSet(NetBoxModelFilterSet):
    cluster_id = django_filters.ModelMultipleChoiceFilter(
        queryset=NetAppCluster.objects.all(),
        field_name='node__cluster',
        label='Cluster (ID)',
    )
    cluster = django_filters.ModelMultipleChoiceFilter(
        queryset=NetAppCluster.objects.all(),
        field_name='node__cluster__name',
        to_field_name='name',
        label='Cluster (Name)',
    )
    svm = django_filters.ModelChoiceFilter(
        queryset=NetAppSVM.objects.all(),
        method='filter_svm',
        label='SVM',
    )

    class Meta:
        model = NetAppAggregate
        fields = ("id", "name", "node", "uuid")

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(uuid__icontains=value)
            | Q(node__name__icontains=value)
        )

    def filter_svm(self, queryset, name, value):
        if not value or not value.cluster_id:
            return queryset
        return queryset.filter(node__cluster_id=value.cluster_id)


class SVMFilterSet(NetBoxModelFilterSet):
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        field_name='tenant',
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        field_name='tenant__slug',
        to_field_name='slug',
        label='Tenant (Slug)',
    )

    class Meta:
        model = NetAppSVM
        fields = ("id", "name", "cluster", "tenant", "uuid")

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(uuid__icontains=value)
        )


class VolumeFilterSet(NetBoxModelFilterSet):
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        method='filter_tenant',
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        method='filter_tenant',
        to_field_name='slug',
        label='Tenant (Slug)',
    )

    class Meta:
        model = NetAppVolume
        fields = ("id", "name", "svm", "aggregate", "size", "tenant", "uuid")

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(uuid__icontains=value)
            | Q(svm__name__icontains=value)
            | Q(svm__uuid__icontains=value)
        )

    def filter_tenant(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.for_tenant(value).distinct()


class QTreeFilterSet(NetBoxModelFilterSet):
    svm_id = django_filters.ModelMultipleChoiceFilter(
        queryset=NetAppSVM.objects.all(),
        field_name='volume__svm',
        label='SVM (ID)'
    )
    svm = django_filters.ModelMultipleChoiceFilter(
        queryset=NetAppSVM.objects.all(),
        field_name='volume__svm__name',
        to_field_name='name',
        label='SVM (Name)'
    )

    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        method='filter_tenant',
        label='Tenant (ID)',
    )
    tenant =  django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        method='filter_tenant',
        to_field_name='slug',
        label='Tenant (Slug)'
    )

    class Meta:
        model = NetAppQTree
        fields = ("id", "name", "volume")

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(volume__name__icontains=value)
            | Q(volume__uuid__icontains=value)
        )

    def filter_tenant(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(volume__in=NetAppVolume.objects.for_tenant(value)).distinct()


class QuotaFilterSet(NetBoxModelFilterSet):
    svm = django_filters.ModelMultipleChoiceFilter(
        queryset=NetAppSVM.objects.all(),
        field_name='volume__svm__name',
        to_field_name='name',
        label='SVM (Name)'
    )
    svm_id = django_filters.ModelMultipleChoiceFilter(
        queryset=NetAppSVM.objects.all(),
        field_name='volume__svm',
    )

    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        method='filter_tenant',
        label='Tenant (ID)',
    )
    tenant =  django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        method='filter_tenant',
        to_field_name='slug',
        label='Tenant (Slug)'
    )

    class Meta:
        model = NetAppQuota
        fields = ("id", "volume", "qtree", "index")

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(index__icontains=value)
            | Q(volume__name__icontains=value)
            | Q(volume__uuid__icontains=value)
            | Q(qtree__name__icontains=value)
        )

    def filter_tenant(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(volume__in=NetAppVolume.objects.for_tenant(value)).distinct()


class LUNFilterSet(NetBoxModelFilterSet):
    tenant_id = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        method='filter_tenant',
        label='Tenant (ID)',
    )
    tenant = django_filters.ModelMultipleChoiceFilter(
        queryset=Tenant.objects.all(),
        method='filter_tenant',
        to_field_name='slug',
        label='Tenant (Slug)',
    )

    class Meta:
        model = NetAppLUN
        fields = ("id", "name", "tenant", "volume", "qtree", "wwn", "os_type", "uuid")

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(uuid__icontains=value)
            | Q(wwn__icontains=value)
            | Q(volume__name__icontains=value)
            | Q(volume__uuid__icontains=value)
            | Q(volume__svm__name__icontains=value)
            | Q(volume__svm__uuid__icontains=value)
            | Q(qtree__name__icontains=value)
        )

    def filter_tenant(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.for_tenant(value).distinct()
