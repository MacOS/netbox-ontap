# SPDX-FileCopyrightText: 2026 Gabor Somogyvari, Leonhard Kreißig (Deutsche Telekom AG) <leonhard.kreissig@telekom.de>
#
# SPDX-License-Identifier: Apache-2.0

from netbox.views import generic
from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from django.views import View
from dcim.models import Device
from tenancy.models import Tenant
from utilities.views import ViewTab, register_model_view

from . import filtersets, forms, models, tables


@register_model_view(Device, 'ontap_node', path='ontap-node')
class DeviceNetAppNodeView(View):
    tab = ViewTab(
        label='NetApp Node',
        visible=lambda obj: hasattr(obj, 'ontap_node'),
    )

    def get(self, request, pk):
        device = get_object_or_404(Device.objects.restrict(request.user, 'view'), pk=pk)
        node = getattr(device, 'ontap_node', None)

        return render(request, 'netbox_ontap/device_ontap_node.html', {
            'object': device,
            'tab': self.tab,
            'node': node,
        })


class ClusterView(generic.ObjectView):
    queryset = models.NetAppCluster.objects.all()

    def get_extra_context(self, request, instance):
        nodes = instance.ontap_nodes.all()

        nodes_table = tables.NodeTable(nodes)
        nodes_table.configure(request)

        aggregates_table = tables.AggregateTable(models.NetAppAggregate.objects.filter(node__in=nodes))
        aggregates_table.configure(request)

        svms_table = tables.SVMTable(instance.ontap_svms.all())
        svms_table.configure(request)

        return {
            "nodes_table": nodes_table,
            "aggregates_table": aggregates_table,
            "svms_table": svms_table,
        }


class ClusterListView(generic.ObjectListView):
    queryset = models.NetAppCluster.objects.all()
    table = tables.ClusterTable
    filterset = filtersets.ClusterFilterSet
    filterset_form = forms.ClusterFilterForm


class ClusterEditView(generic.ObjectEditView):
    queryset = models.NetAppCluster.objects.all()
    form = forms.ClusterForm


class ClusterDeleteView(generic.ObjectDeleteView):
    queryset = models.NetAppCluster.objects.all()


class ClusterBulkDeleteView(generic.BulkDeleteView):
    queryset = models.NetAppCluster.objects.all()
    table = tables.ClusterTable
    filterset = filtersets.ClusterFilterSet


class ClusterImportView(generic.BulkImportView):
    queryset = models.NetAppCluster.objects.all()
    model_form = forms.ClusterCSVForm
    table = tables.ClusterTable


class NodeView(generic.ObjectView):
    queryset = models.NetAppNode.objects.all()

    def get_extra_context(self, request, instance):
        aggregates_table = tables.AggregateTable(instance.ontap_aggregates.all())
        aggregates_table.configure(request)

        return {
            "aggregates_table": aggregates_table,
        }


class NodeListView(generic.ObjectListView):
    queryset = models.NetAppNode.objects.all()
    table = tables.NodeTable
    filterset = filtersets.NodeFilterSet
    filterset_form = forms.NodeFilterForm


class NodeEditView(generic.ObjectEditView):
    queryset = models.NetAppNode.objects.all()
    form = forms.NodeForm


class NodeDeleteView(generic.ObjectDeleteView):
    queryset = models.NetAppNode.objects.all()


class NodeBulkDeleteView(generic.BulkDeleteView):
    queryset = models.NetAppNode.objects.all()
    table = tables.NodeTable
    filterset = filtersets.NodeFilterSet


class NodeImportView(generic.BulkImportView):
    queryset = models.NetAppNode.objects.all()
    model_form = forms.NodeCSVForm
    table = tables.NodeTable


class AggregateView(generic.ObjectView):
    queryset = models.NetAppAggregate.objects.all()

    def get_extra_context(self, request, instance):
        volumes_table = tables.VolumeTable(instance.ontap_volumes.all())
        volumes_table.configure(request)

        return {
            "volumes_table": volumes_table,
        }


class AggregateListView(generic.ObjectListView):
    queryset = models.NetAppAggregate.objects.all()
    table = tables.AggregateTable
    filterset = filtersets.AggregateFilterSet
    filterset_form = forms.AggregateFilterForm


class AggregateEditView(generic.ObjectEditView):
    queryset = models.NetAppAggregate.objects.all()
    form = forms.AggregateForm


class AggregateDeleteView(generic.ObjectDeleteView):
    queryset = models.NetAppAggregate.objects.all()


class AggregateBulkDeleteView(generic.BulkDeleteView):
    queryset = models.NetAppAggregate.objects.all()
    table = tables.AggregateTable
    filterset = filtersets.AggregateFilterSet


class AggregateImportView(generic.BulkImportView):
    queryset = models.NetAppAggregate.objects.all()
    model_form = forms.AggregateCSVForm
    table = tables.AggregateTable


class SVMView(generic.ObjectView):
    queryset = models.NetAppSVM.objects.all()

    def get_extra_context(self, request, instance):
        volumes = instance.ontap_volumes.all()

        tenant_owners = (
            Tenant.objects.filter(
                Q(ontap_svms=instance)
                | Q(ontap_volumes__svm=instance)
                | Q(ontap_luns__volume__svm=instance)
                | Q(ontap_luns__qtree__volume__svm=instance)
            )
            .distinct()
            .order_by("name")
        )

        volumes_table = tables.VolumeTable(volumes)
        volumes_table.configure(request)

        qtrees_table = tables.QTreeTable(models.NetAppQTree.objects.filter(volume__in=volumes).distinct())
        qtrees_table.configure(request)

        quotas_table = tables.QuotaTable(models.NetAppQuota.objects.filter(volume__in=volumes).distinct())
        quotas_table.configure(request)

        luns_table = tables.LUNTable(
            models.NetAppLUN.objects.filter(Q(volume__in=volumes) | Q(qtree__volume__in=volumes)).distinct()
        )
        luns_table.configure(request)

        return {
            "tenant_owners": tenant_owners,
            "volumes_table": volumes_table,
            "qtrees_table": qtrees_table,
            "quotas_table": quotas_table,
            "luns_table": luns_table,
        }


class SVMListView(generic.ObjectListView):
    queryset = models.NetAppSVM.objects.all()
    table = tables.SVMTable
    filterset = filtersets.SVMFilterSet
    filterset_form = forms.SVMFilterForm


class SVMEditView(generic.ObjectEditView):
    queryset = models.NetAppSVM.objects.all()
    form = forms.SVMForm


class SVMDeleteView(generic.ObjectDeleteView):
    queryset = models.NetAppSVM.objects.all()


class SVMBulkDeleteView(generic.BulkDeleteView):
    queryset = models.NetAppSVM.objects.all()
    table = tables.SVMTable
    filterset = filtersets.SVMFilterSet


class SVMImportView(generic.BulkImportView):
    queryset = models.NetAppSVM.objects.all()
    model_form = forms.SVMCSVForm
    table = tables.SVMTable


class VolumeView(generic.ObjectView):
    queryset = models.NetAppVolume.objects.all()

    def get_extra_context(self, request, instance):
        qtrees_table = tables.QTreeTable(instance.ontap_qtrees.all())
        qtrees_table.configure(request)

        luns_table = tables.LUNTable(models.NetAppLUN.objects.filter(Q(volume=instance) | Q(qtree__volume=instance)).distinct())
        luns_table.configure(request)

        return {
            "qtrees_table": qtrees_table,
            "luns_table": luns_table,
        }


class VolumeListView(generic.ObjectListView):
    queryset = models.NetAppVolume.objects.all()
    table = tables.VolumeTable
    filterset = filtersets.VolumeFilterSet
    filterset_form = forms.VolumeFilterForm


class VolumeEditView(generic.ObjectEditView):
    queryset = models.NetAppVolume.objects.all()
    form = forms.VolumeForm


class VolumeDeleteView(generic.ObjectDeleteView):
    queryset = models.NetAppVolume.objects.all()


class VolumeBulkDeleteView(generic.BulkDeleteView):
    queryset = models.NetAppVolume.objects.all()
    table = tables.VolumeTable
    filterset = filtersets.VolumeFilterSet


class VolumeImportView(generic.BulkImportView):
    queryset = models.NetAppVolume.objects.all()
    model_form = forms.VolumeCSVForm
    table = tables.VolumeTable


class QTreeView(generic.ObjectView):
    queryset = models.NetAppQTree.objects.all()

    def get_extra_context(self, request, instance):
        quotas_table = tables.QuotaTable(instance.ontap_quotas.all())
        quotas_table.configure(request)

        luns_table = tables.LUNTable(instance.ontap_luns.all())
        luns_table.configure(request)

        return {
            "quotas_table": quotas_table,
            "luns_table": luns_table,
        }


class QTreeListView(generic.ObjectListView):
    queryset = models.NetAppQTree.objects.all()
    table = tables.QTreeTable
    filterset = filtersets.QTreeFilterSet
    filterset_form = forms.QTreeFilterForm


class QTreeEditView(generic.ObjectEditView):
    queryset = models.NetAppQTree.objects.all()
    form = forms.QTreeForm


class QTreeDeleteView(generic.ObjectDeleteView):
    queryset = models.NetAppQTree.objects.all()


class QTreeBulkDeleteView(generic.BulkDeleteView):
    queryset = models.NetAppQTree.objects.all()
    table = tables.QTreeTable
    filterset = filtersets.QTreeFilterSet


class QTreeImportView(generic.BulkImportView):
    queryset = models.NetAppQTree.objects.all()
    model_form = forms.QTreeCSVForm
    table = tables.QTreeTable


class QuotaView(generic.ObjectView):
    queryset = models.NetAppQuota.objects.all()


class QuotaListView(generic.ObjectListView):
    queryset = models.NetAppQuota.objects.all()
    table = tables.QuotaTable
    filterset = filtersets.QuotaFilterSet
    filterset_form = forms.QuotaFilterForm


class QuotaEditView(generic.ObjectEditView):
    queryset = models.NetAppQuota.objects.all()
    form = forms.QuotaForm


class QuotaDeleteView(generic.ObjectDeleteView):
    queryset = models.NetAppQuota.objects.all()


class QuotaBulkDeleteView(generic.BulkDeleteView):
    queryset = models.NetAppQuota.objects.all()
    table = tables.QuotaTable
    filterset = filtersets.QuotaFilterSet


class QuotaImportView(generic.BulkImportView):
    queryset = models.NetAppQuota.objects.all()
    model_form = forms.QuotaCSVForm
    table = tables.QuotaTable


class LUNView(generic.ObjectView):
    queryset = models.NetAppLUN.objects.all()


class LUNListView(generic.ObjectListView):
    queryset = models.NetAppLUN.objects.all()
    table = tables.LUNTable
    filterset = filtersets.LUNFilterSet
    filterset_form = forms.LUNFilterForm


class LUNEditView(generic.ObjectEditView):
    queryset = models.NetAppLUN.objects.all()
    form = forms.LUNForm


class LUNDeleteView(generic.ObjectDeleteView):
    queryset = models.NetAppLUN.objects.all()


class LUNBulkDeleteView(generic.BulkDeleteView):
    queryset = models.NetAppLUN.objects.all()
    table = tables.LUNTable
    filterset = filtersets.LUNFilterSet


class LUNImportView(generic.BulkImportView):
    queryset = models.NetAppLUN.objects.all()
    model_form = forms.LUNCSVForm
    table = tables.LUNTable
