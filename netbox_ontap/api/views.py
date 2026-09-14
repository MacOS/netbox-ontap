# SPDX-FileCopyrightText: 2026 Gabor Somogyvari, Leonhard Kreißig (Deutsche Telekom AG) <leonhard.kreissig@telekom.de>
#
# SPDX-License-Identifier: Apache-2.0

from netbox.api.viewsets import NetBoxModelViewSet

from .. import filtersets, models
from .serializers import (
    NetAppAggregateSerializer,
    NetAppClusterSerializer,
    NetAppLUNSerializer,
    NetAppNodeSerializer,
    NetAppQTreeSerializer,
    NetAppQuotaSerializer,
    NetAppSVMSerializer,
    NetAppVolumeSerializer,
)


class ClusterViewSet(NetBoxModelViewSet):
    queryset = models.NetAppCluster.objects.select_related("management_ip").prefetch_related("tags")
    serializer_class = NetAppClusterSerializer
    filterset_class = filtersets.ClusterFilterSet


class NodeViewSet(NetBoxModelViewSet):
    queryset = models.NetAppNode.objects.select_related(
        "cluster", "device", "management_ip",
        "ha_pair_as_node_a__node_b",
        "ha_pair_as_node_b__node_a",
    ).prefetch_related("tags")
    serializer_class = NetAppNodeSerializer
    filterset_class = filtersets.NodeFilterSet


class AggregateViewSet(NetBoxModelViewSet):
    queryset = models.NetAppAggregate.objects.select_related("node", "node__cluster").prefetch_related("tags")
    serializer_class = NetAppAggregateSerializer
    filterset_class = filtersets.AggregateFilterSet


class SVMViewSet(NetBoxModelViewSet):
    queryset = models.NetAppSVM.objects.select_related("cluster", "tenant").prefetch_related("tags")
    serializer_class = NetAppSVMSerializer
    filterset_class = filtersets.SVMFilterSet


class VolumeViewSet(NetBoxModelViewSet):
    queryset = models.NetAppVolume.objects.select_related(
        "svm", "aggregate", "aggregate__node", "tenant"
    ).prefetch_related("tags")
    serializer_class = NetAppVolumeSerializer
    filterset_class = filtersets.VolumeFilterSet


class QTreeViewSet(NetBoxModelViewSet):
    queryset = models.NetAppQTree.objects.select_related("volume", "volume__svm", "volume__tenant").prefetch_related("tags")
    serializer_class = NetAppQTreeSerializer
    filterset_class = filtersets.QTreeFilterSet


class QuotaViewSet(NetBoxModelViewSet):
    queryset = models.NetAppQuota.objects.select_related("qtree", "qtree__volume", "qtree__volume__svm").prefetch_related("tags")
    serializer_class = NetAppQuotaSerializer 
    filterset_class = filtersets.QuotaFilterSet


class LUNViewSet(NetBoxModelViewSet):
    queryset = models.NetAppLUN.objects.select_related("tenant", "volume", "volume__svm", "qtree", "qtree__volume").prefetch_related("tags")
    serializer_class = NetAppLUNSerializer
    filterset_class = filtersets.LUNFilterSet
