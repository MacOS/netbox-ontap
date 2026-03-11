from django import forms

from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm, NetBoxModelImportForm
from utilities.forms.fields import (
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
)
from tenancy.models import Tenant
from virtualization.models import Cluster

from .models import LUN, QTree, Quota, SVM, Volume


#
# Regular forms
#

class SVMForm(NetBoxModelForm):
    cluster = DynamicModelChoiceField(queryset=Cluster.objects.all(), required=False)
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    class Meta:
        model = SVM
        fields = ("name", "cluster", "tenant", "uuid", "description", "tags")


class VolumeForm(NetBoxModelForm):
    svm = DynamicModelChoiceField(queryset=SVM.objects.all())
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    class Meta:
        model = Volume
        fields = ("name", "svm", "tenant", "uuid", "description", "tags")


class QTreeForm(NetBoxModelForm):
    volume = DynamicModelChoiceField(queryset=Volume.objects.all())

    class Meta:
        model = QTree
        fields = ("name", "volume", "uuid", "description", "tags")


class QuotaForm(NetBoxModelForm):
    qtree = DynamicModelChoiceField(queryset=QTree.objects.all(), required=False)

    class Meta:
        model = Quota
        fields = ("qtree", "size", "index", "description", "tags")


class LUNForm(NetBoxModelForm):
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)
    svm = DynamicModelChoiceField(queryset=SVM.objects.all(), required=False)
    qtree = DynamicModelChoiceField(queryset=QTree.objects.all(), required=False)

    class Meta:
        model = LUN
        fields = ("name", "tenant", "svm", "qtree", "size", "wwn", "uuid", "description", "tags")


#
# Filter forms
#

class SVMFilterForm(NetBoxModelFilterSetForm):
    model = SVM
    cluster = DynamicModelMultipleChoiceField(queryset=Cluster.objects.all(), required=False)
    tenant = DynamicModelMultipleChoiceField(queryset=Tenant.objects.all(), required=False)
    name = forms.CharField(required=False)
    uuid = forms.CharField(required=False, label="ONTAP SVM UUID")


class VolumeFilterForm(NetBoxModelFilterSetForm):
    model = Volume
    svm = DynamicModelMultipleChoiceField(queryset=SVM.objects.all(), required=False)
    tenant = DynamicModelMultipleChoiceField(queryset=Tenant.objects.all(), required=False)
    name = forms.CharField(required=False)
    uuid = forms.CharField(required=False, label="ONTAP Volume UUID")


class QTreeFilterForm(NetBoxModelFilterSetForm):
    model = QTree
    volume = DynamicModelMultipleChoiceField(queryset=Volume.objects.all(), required=False)
    name = forms.CharField(required=False)
    uuid = forms.CharField(required=False, label="ONTAP QTree UUID")


class QuotaFilterForm(NetBoxModelFilterSetForm):
    model = Quota
    qtree = DynamicModelMultipleChoiceField(queryset=QTree.objects.all(), required=False)
    index = forms.CharField(required=False, label="Quota Index")


class LUNFilterForm(NetBoxModelFilterSetForm):
    model = LUN
    tenant = DynamicModelMultipleChoiceField(queryset=Tenant.objects.all(), required=False)
    svm = DynamicModelMultipleChoiceField(queryset=SVM.objects.all(), required=False)
    qtree = DynamicModelMultipleChoiceField(queryset=QTree.objects.all(), required=False)
    name = forms.CharField(required=False)
    wwn = forms.CharField(required=False, label="WWN")
    uuid = forms.CharField(required=False, label="ONTAP LUN UUID")


#
# CSV forms
#

class SVMCSVForm(NetBoxModelImportForm):
    cluster = CSVModelChoiceField(queryset=Cluster.objects.all(), to_field_name="name")
    tenant = CSVModelChoiceField(queryset=Tenant.objects.all(), to_field_name="name", required=False)

    class Meta:
        model = SVM
        fields = ("name", "cluster", "tenant", "uuid", "description")


class VolumeCSVForm(NetBoxModelImportForm):
    svm = CSVModelChoiceField(queryset=SVM.objects.all(), to_field_name="name")
    tenant = CSVModelChoiceField(queryset=Tenant.objects.all(), to_field_name="name", required=False)

    class Meta:
        model = Volume
        fields = ("name", "svm", "tenant", "uuid", "description")


class QTreeCSVForm(NetBoxModelImportForm):
    volume = CSVModelChoiceField(queryset=Volume.objects.all(), to_field_name="name")

    class Meta:
        model = QTree
        fields = ("name", "volume", "uuid", "description")


class QuotaCSVForm(NetBoxModelImportForm):
    qtree = CSVModelChoiceField(queryset=QTree.objects.all(), to_field_name="name", required=False)

    class Meta:
        model = Quota
        fields = ("qtree", "size", "index", "description")


class LUNCSVForm(NetBoxModelImportForm):
    tenant = CSVModelChoiceField(queryset=Tenant.objects.all(), to_field_name="name", required=False)
    svm = CSVModelChoiceField(queryset=SVM.objects.all(), to_field_name="name", required=False)
    qtree = CSVModelChoiceField(queryset=QTree.objects.all(), to_field_name="name", required=False)

    class Meta:
        model = LUN
        fields = ("name", "tenant", "svm", "qtree", "size", "wwn", "uuid", "description")
