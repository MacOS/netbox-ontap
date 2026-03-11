from netbox.views import generic
from django.db.models import Q

from . import filtersets, forms, models, tables


class SVMView(generic.ObjectView):
    queryset = models.SVM.objects.all()

    def get_extra_context(self, request, instance):
        volumes_table = tables.VolumeTable(instance.volumes.all())
        volumes_table.configure(request)

        luns_table = tables.LUNTable(models.LUN.objects.filter(volume__svm=instance).distinct())
        luns_table.configure(request)

        return {
            "volumes_table": volumes_table,
            "luns_table": luns_table,
        }


class SVMListView(generic.ObjectListView):
    queryset = models.SVM.objects.all()
    table = tables.SVMTable
    filterset = filtersets.SVMFilterSet
    filterset_form = forms.SVMFilterForm


class SVMEditView(generic.ObjectEditView):
    queryset = models.SVM.objects.all()
    form = forms.SVMForm


class SVMDeleteView(generic.ObjectDeleteView):
    queryset = models.SVM.objects.all()


class SVMBulkDeleteView(generic.BulkDeleteView):
    queryset = models.SVM.objects.all()
    table = tables.SVMTable
    filterset = filtersets.SVMFilterSet


class SVMImportView(generic.BulkImportView):
    queryset = models.SVM.objects.all()
    model_form = forms.SVMCSVForm
    table = tables.SVMTable


class VolumeView(generic.ObjectView):
    queryset = models.Volume.objects.all()

    def get_extra_context(self, request, instance):
        qtrees_table = tables.QTreeTable(instance.qtrees.all())
        qtrees_table.configure(request)

        luns_table = tables.LUNTable(models.LUN.objects.filter(Q(volume=instance) | Q(qtree__volume=instance)).distinct())
        luns_table.configure(request)

        return {
            "qtrees_table": qtrees_table,
            "luns_table": luns_table,
        }


class VolumeListView(generic.ObjectListView):
    queryset = models.Volume.objects.all()
    table = tables.VolumeTable
    filterset = filtersets.VolumeFilterSet
    filterset_form = forms.VolumeFilterForm


class VolumeEditView(generic.ObjectEditView):
    queryset = models.Volume.objects.all()
    form = forms.VolumeForm


class VolumeDeleteView(generic.ObjectDeleteView):
    queryset = models.Volume.objects.all()


class VolumeBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Volume.objects.all()
    table = tables.VolumeTable
    filterset = filtersets.VolumeFilterSet


class VolumeImportView(generic.BulkImportView):
    queryset = models.Volume.objects.all()
    model_form = forms.VolumeCSVForm
    table = tables.VolumeTable


class QTreeView(generic.ObjectView):
    queryset = models.QTree.objects.all()

    def get_extra_context(self, request, instance):
        quotas_table = tables.QuotaTable(instance.quotas.all())
        quotas_table.configure(request)

        luns_table = tables.LUNTable(instance.luns.all())
        luns_table.configure(request)

        return {
            "quotas_table": quotas_table,
            "luns_table": luns_table,
        }


class QTreeListView(generic.ObjectListView):
    queryset = models.QTree.objects.all()
    table = tables.QTreeTable
    filterset = filtersets.QTreeFilterSet
    filterset_form = forms.QTreeFilterForm


class QTreeEditView(generic.ObjectEditView):
    queryset = models.QTree.objects.all()
    form = forms.QTreeForm


class QTreeDeleteView(generic.ObjectDeleteView):
    queryset = models.QTree.objects.all()


class QTreeBulkDeleteView(generic.BulkDeleteView):
    queryset = models.QTree.objects.all()
    table = tables.QTreeTable
    filterset = filtersets.QTreeFilterSet


class QTreeImportView(generic.BulkImportView):
    queryset = models.QTree.objects.all()
    model_form = forms.QTreeCSVForm
    table = tables.QTreeTable


class QuotaView(generic.ObjectView):
    queryset = models.Quota.objects.all()


class QuotaListView(generic.ObjectListView):
    queryset = models.Quota.objects.all()
    table = tables.QuotaTable
    filterset = filtersets.QuotaFilterSet
    filterset_form = forms.QuotaFilterForm


class QuotaEditView(generic.ObjectEditView):
    queryset = models.Quota.objects.all()
    form = forms.QuotaForm


class QuotaDeleteView(generic.ObjectDeleteView):
    queryset = models.Quota.objects.all()


class QuotaBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Quota.objects.all()
    table = tables.QuotaTable
    filterset = filtersets.QuotaFilterSet


class QuotaImportView(generic.BulkImportView):
    queryset = models.Quota.objects.all()
    model_form = forms.QuotaCSVForm
    table = tables.QuotaTable


class LUNView(generic.ObjectView):
    queryset = models.LUN.objects.all()


class LUNListView(generic.ObjectListView):
    queryset = models.LUN.objects.all()
    table = tables.LUNTable
    filterset = filtersets.LUNFilterSet
    filterset_form = forms.LUNFilterForm


class LUNEditView(generic.ObjectEditView):
    queryset = models.LUN.objects.all()
    form = forms.LUNForm


class LUNDeleteView(generic.ObjectDeleteView):
    queryset = models.LUN.objects.all()


class LUNBulkDeleteView(generic.BulkDeleteView):
    queryset = models.LUN.objects.all()
    table = tables.LUNTable
    filterset = filtersets.LUNFilterSet


class LUNImportView(generic.BulkImportView):
    queryset = models.LUN.objects.all()
    model_form = forms.LUNCSVForm
    table = tables.LUNTable
