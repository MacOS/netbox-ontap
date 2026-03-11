from netbox.api.viewsets import NetBoxModelViewSet

from .. import filtersets, models
from .serializers import LUNSerializer, QTreeSerializer, QuotaSerializer, SVMSerializer, VolumeSerializer


class SVMViewSet(NetBoxModelViewSet):
    queryset = models.SVM.objects.select_related("cluster", "tenant").prefetch_related("tags")
    serializer_class = SVMSerializer
    filterset_class = filtersets.SVMFilterSet


class VolumeViewSet(NetBoxModelViewSet):
    queryset = models.Volume.objects.select_related("svm", "tenant").prefetch_related("tags")
    serializer_class = VolumeSerializer
    filterset_class = filtersets.VolumeFilterSet


class QTreeViewSet(NetBoxModelViewSet):
    queryset = models.QTree.objects.select_related("volume", "volume__svm", "volume__tenant").prefetch_related("tags")
    serializer_class = QTreeSerializer
    filterset_class = filtersets.QTreeFilterSet


class QuotaViewSet(NetBoxModelViewSet):
    queryset = models.Quota.objects.select_related("qtree", "qtree__volume", "qtree__volume__svm").prefetch_related("tags")
    serializer_class = QuotaSerializer
    filterset_class = filtersets.QuotaFilterSet


class LUNViewSet(NetBoxModelViewSet):
    queryset = models.LUN.objects.select_related("tenant", "volume", "volume__svm", "qtree", "qtree__volume").prefetch_related("tags")
    serializer_class = LUNSerializer
    filterset_class = filtersets.LUNFilterSet
