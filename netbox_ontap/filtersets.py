from netbox.filtersets import NetBoxModelFilterSet
from django.db.models import Q
import django_filters

from tenancy.models import Tenant

from .models import LUN, QTree, Quota, SVM, Volume


class SVMFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = SVM
        fields = ("id", "name", "cluster", "tenant", "uuid")

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(uuid__icontains=value)
        )


class VolumeFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = Volume
        fields = ("id", "name", "svm", "tenant", "uuid")

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(uuid__icontains=value)
            | Q(svm__name__icontains=value)
            | Q(svm__uuid__icontains=value)
        )


class QTreeFilterSet(NetBoxModelFilterSet):
    svm_id = django_filters.ModelMultipleChoiceFilter(
        queryset=SVM.objects.all(),
        field_name='volume__svm',
        label='SVM (ID)'
    )
    svm = django_filters.ModelMultipleChoiceFilter(
        queryset=SVM.objects.all(),
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
        to_field_nam='slug',
        tabel='Tenant (Slug)'
    )

    class Meta:
        model = QTree
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

        return queryset.filter(
            Q(volume__tenant__in=value) | Q(volume__svm__tenant__in=value)
        ).distinct()


class QuotaFilterSet(NetBoxModelFilterSet):
    svm = django_filters.ModelMultipleChoiceFilter(
        queryset=SVM.objects.all(),
        field_name='volume__svm__name',
        to_field_name='name',
        label='SVM (Name)'
    )
    svm_id = django_filters.ModelMultipleChoiceFilter(
        queryset=SVM.objects.all(),
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
        to_field_nam='slug',
        tabel='Tenant (Slug)'
    )

    class Meta:
        model = Quota
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
        return queryset.filter(
            Q(volume__tenant__in=value) | Q(volume__svm__tenant__in=value)
        ).distinct()


class LUNFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = LUN
        fields = ("id", "name", "tenant", "volume", "qtree", "wwn", "uuid")

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
