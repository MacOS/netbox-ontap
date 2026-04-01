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
        fields = ("name", "volume", "description", "tags")


class QuotaForm(NetBoxModelForm):
    volume = DynamicModelChoiceField(queryset=Volume.objects.all())
    qtree = DynamicModelChoiceField(
        queryset=QTree.objects.all(),
        required=False,
        query_params={"volume": "$volume"},
    )

    def clean(self):
        cleaned_data = super().clean()
        volume = cleaned_data.get("volume")
        qtree = cleaned_data.get("qtree")

        # Keep volume and qtree aligned in the form UX.
        if qtree and (not volume or qtree.volume_id != volume.id):
            cleaned_data["volume"] = qtree.volume

        return cleaned_data

    class Meta:
        model = Quota
        fields = ("volume", "qtree", "size", "index", "description", "tags")


class LUNForm(NetBoxModelForm):
    volume = DynamicModelChoiceField(queryset=Volume.objects.all())
    qtree = DynamicModelChoiceField(
        queryset=QTree.objects.all(),
        required=False,
        query_params={"volume": "$volume"},
    )

    def clean(self):
        cleaned_data = super().clean()
        volume = cleaned_data.get("volume")
        qtree = cleaned_data.get("qtree")

        if qtree and (not volume or qtree.volume_id != volume.id):
            cleaned_data["volume"] = qtree.volume

        return cleaned_data

    class Meta:
        model = LUN
        fields = ("name", "volume", "qtree", "size", "wwn", "uuid", "description", "tags")


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
    svm_id = DynamicModelMultipleChoiceField(
        queryset=SVM.objects.all(),
        required=False,
        label='SVM'
    )
    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label='Tenant'
    )


class QuotaFilterForm(NetBoxModelFilterSetForm):
    model = Quota
    volume = DynamicModelMultipleChoiceField(queryset=Volume.objects.all(), required=False)
    qtree = DynamicModelMultipleChoiceField(queryset=QTree.objects.all(), required=False)
    index = forms.CharField(required=False, label="Quota Index")
    svm_id = DynamicModelMultipleChoiceField(
        queryset=SVM.objects.all(),
        required=False,
        label='SVM'
    )
    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label='Tenant'
    )


class LUNFilterForm(NetBoxModelFilterSetForm):
    model = LUN
    tenant = DynamicModelMultipleChoiceField(queryset=Tenant.objects.all(), required=False)
    volume = DynamicModelMultipleChoiceField(queryset=Volume.objects.all(), required=False)
    qtree = DynamicModelMultipleChoiceField(queryset=QTree.objects.all(), required=False)
    name = forms.CharField(required=False)
    wwn = forms.CharField(required=False, label="WWN")
    uuid = forms.CharField(required=False, label="ONTAP LUN UUID")
    svm_id = DynamicModelMultipleChoiceField(
        queryset=SVM.objects.all(),
        required=False,
        label='SVM'
    )


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
        fields = ("name", "volume", "description")


class QuotaCSVForm(NetBoxModelImportForm):
    volume = CSVModelChoiceField(queryset=Volume.objects.all(), to_field_name="name")
    qtree = CSVModelChoiceField(queryset=QTree.objects.all(), to_field_name="name", required=False)

    class Meta:
        model = Quota
        fields = ("volume", "qtree", "size", "index", "description")


class LUNCSVForm(NetBoxModelImportForm):
    volume = CSVModelChoiceField(queryset=Volume.objects.all(), to_field_name="name")
    qtree = CSVModelChoiceField(queryset=QTree.objects.all(), to_field_name="name", required=False)

    class Meta:
        model = LUN
        fields = ("name", "volume", "qtree", "size", "wwn", "uuid", "description")
