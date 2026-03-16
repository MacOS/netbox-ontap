from netbox.filtersets import NetBoxModelFilterSet
from django.db.models import Q

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
    class Meta:
        model = QTree
        fields = ("id", "name", "volume")

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value)
            | Q(volume__name__icontains=value)
            | Q(volume__uuid__icontains=value)
        )


class QuotaFilterSet(NetBoxModelFilterSet):
    class Meta:
        model = Quota
        fields = ("id", "qtree", "index")

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(index__icontains=value)
            | Q(qtree__name__icontains=value)
            | Q(qtree__volume__name__icontains=value)
            | Q(qtree__volume__uuid__icontains=value)
        )


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
