# SPDX-FileCopyrightText: 2026 Gabor Somogyvari, Leonhard Kreißig (Deutsche Telekom AG) <leonhard.kreissig@telekom.de>
#
# SPDX-License-Identifier: Apache-2.0

from django import forms

from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm, NetBoxModelImportForm
from utilities.forms.fields import (
    CSVModelChoiceField,
    DynamicModelChoiceField,
    DynamicModelMultipleChoiceField,
)
from dcim.models import Device
from ipam.models import IPAddress
from tenancy.models import Tenant

from .models import (
    NetAppAggregate,
    NetAppCluster,
    NetAppHAPair,
    NetAppLUN,
    NetAppNode,
    NetAppQTree,
    NetAppQuota,
    NetAppSVM,
    NetAppVolume,
)


#
# Regular forms
#

class ClusterForm(NetBoxModelForm):
    management_ip = DynamicModelChoiceField(queryset=IPAddress.objects.all(), required=False)

    class Meta:
        model = NetAppCluster
        fields = ("name", "management_ip", "ontap_version", "uuid", "description", "tags")


class NodeForm(NetBoxModelForm):
    cluster = DynamicModelChoiceField(queryset=NetAppCluster.objects.all())
    device = DynamicModelChoiceField(queryset=Device.objects.all(), required=False)
    management_ip = DynamicModelChoiceField(queryset=IPAddress.objects.all(), required=False)
    ha_partner = DynamicModelChoiceField(
        queryset=NetAppNode.objects.all(),
        required=False,
        label='HA Partner',
        query_params={'cluster': '$cluster'},
    )

    class Meta:
        model = NetAppNode
        fields = (
            "name",
            "cluster",
            "device",
            "model",
            "serial_number",
            "management_ip",
            "uuid",
            "description",
            "tags",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            partner = self.instance.ha_partner
            self.fields['ha_partner'].initial = partner.pk if partner else None
            # Exclude self from selectable partners.
            self.fields['ha_partner'].queryset = NetAppNode.objects.exclude(pk=self.instance.pk)

    def save(self, commit=True):
        node = super().save(commit=commit)
        if commit:
            self._sync_ha_partner(node)
        return node

    def _sync_ha_partner(self, node):
        """Create, replace, or remove the HA pair to match the selected partner."""
        new_partner = self.cleaned_data.get('ha_partner')
        existing_pair = node.ha_pair

        if existing_pair is not None:
            current_partner = (
                existing_pair.node_b if existing_pair.node_a_id == node.pk else existing_pair.node_a
            )
        else:
            current_partner = None

        if new_partner == current_partner:
            return

        if existing_pair is not None:
            existing_pair.delete()

        if new_partner is not None:
            NetAppHAPair.objects.create(node_a=node, node_b=new_partner)



class AggregateForm(NetBoxModelForm):
    node = DynamicModelChoiceField(queryset=NetAppNode.objects.all())

    class Meta:
        model = NetAppAggregate
        fields = ("name", "node", "size", "uuid", "description", "tags")


class SVMForm(NetBoxModelForm):
    cluster = DynamicModelChoiceField(queryset=NetAppCluster.objects.all(), required=False)
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    class Meta:
        model = NetAppSVM
        fields = ("name", "cluster", "tenant", "uuid", "description", "tags")


class VolumeForm(NetBoxModelForm):
    svm = DynamicModelChoiceField(queryset=NetAppSVM.objects.all())
    aggregate = DynamicModelChoiceField(
        queryset=NetAppAggregate.objects.all(),
        query_params={"svm": "$svm"},
    )
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.svm_id and self.instance.svm.get_tenant():
            self.fields['tenant'].disabled = True

    class Meta:
        model = NetAppVolume
        fields = ("name", "svm", "aggregate", "size", "tenant", "uuid", "description", "tags")


class QTreeForm(NetBoxModelForm):
    volume = DynamicModelChoiceField(queryset=NetAppVolume.objects.all())

    class Meta:
        model = NetAppQTree
        fields = ("name", "volume", "description", "tags")


class QuotaForm(NetBoxModelForm):
    volume = DynamicModelChoiceField(queryset=NetAppVolume.objects.all())
    qtree = DynamicModelChoiceField(
        queryset=NetAppQTree.objects.all(),
        required=False,
        query_params={"volume": "$volume"},
    )

    def clean(self):
        super().clean()
        cleaned_data = self.cleaned_data
        volume = cleaned_data.get("volume")
        qtree = cleaned_data.get("qtree")

        # Keep volume and qtree aligned in the form UX.
        if qtree and (not volume or qtree.volume_id != volume.id):
            cleaned_data["volume"] = qtree.volume

        return cleaned_data

    class Meta:
        model = NetAppQuota
        fields = (
            "volume",
            "qtree",
            "space_hard_limit",
            "space_soft_limit",
            "files_hard_limit",
            "files_soft_limit",
            "index",
            "description",
            "tags",
        )


class LUNForm(NetBoxModelForm):
    volume = DynamicModelChoiceField(queryset=NetAppVolume.objects.all())
    qtree = DynamicModelChoiceField(
        queryset=NetAppQTree.objects.all(),
        required=False,
        query_params={"volume": "$volume"},
    )
    tenant = DynamicModelChoiceField(queryset=Tenant.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.volume_id and self.instance.volume.get_tenant():
            self.fields['tenant'].disabled = True

    class Meta:
        model = NetAppLUN
        fields = ("name", "volume", "qtree", "size", "os_type", "wwn", "tenant", "uuid", "description", "tags")


#
# Filter forms
#

class ClusterFilterForm(NetBoxModelFilterSetForm):
    model = NetAppCluster
    name = forms.CharField(required=False)
    uuid = forms.CharField(required=False, label="ONTAP Cluster UUID")


class NodeFilterForm(NetBoxModelFilterSetForm):
    model = NetAppNode
    cluster = DynamicModelMultipleChoiceField(queryset=NetAppCluster.objects.all(), required=False)
    name = forms.CharField(required=False)
    uuid = forms.CharField(required=False, label="ONTAP Node UUID")


class AggregateFilterForm(NetBoxModelFilterSetForm):
    model = NetAppAggregate
    node = DynamicModelMultipleChoiceField(queryset=NetAppNode.objects.all(), required=False)
    cluster_id = DynamicModelMultipleChoiceField(
        queryset=NetAppCluster.objects.all(),
        required=False,
        label='Cluster'
    )
    name = forms.CharField(required=False)
    uuid = forms.CharField(required=False, label="ONTAP Aggregate UUID")


class SVMFilterForm(NetBoxModelFilterSetForm):
    model = NetAppSVM
    cluster = DynamicModelMultipleChoiceField(queryset=NetAppCluster.objects.all(), required=False)
    tenant = DynamicModelMultipleChoiceField(queryset=Tenant.objects.all(), required=False)
    name = forms.CharField(required=False)
    uuid = forms.CharField(required=False, label="ONTAP SVM UUID")


class VolumeFilterForm(NetBoxModelFilterSetForm):
    model = NetAppVolume
    svm = DynamicModelMultipleChoiceField(queryset=NetAppSVM.objects.all(), required=False)
    aggregate = DynamicModelMultipleChoiceField(queryset=NetAppAggregate.objects.all(), required=False)
    tenant = DynamicModelMultipleChoiceField(queryset=Tenant.objects.all(), required=False)
    name = forms.CharField(required=False)
    uuid = forms.CharField(required=False, label="ONTAP Volume UUID")


class QTreeFilterForm(NetBoxModelFilterSetForm):
    model = NetAppQTree
    volume = DynamicModelMultipleChoiceField(queryset=NetAppVolume.objects.all(), required=False)
    name = forms.CharField(required=False)
    svm_id = DynamicModelMultipleChoiceField(
        queryset=NetAppSVM.objects.all(),
        required=False,
        label='SVM'
    )
    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label='Tenant'
    )


class QuotaFilterForm(NetBoxModelFilterSetForm):
    model = NetAppQuota
    volume = DynamicModelMultipleChoiceField(queryset=NetAppVolume.objects.all(), required=False)
    qtree = DynamicModelMultipleChoiceField(queryset=NetAppQTree.objects.all(), required=False)
    index = forms.CharField(required=False, label="Quota Index")
    svm_id = DynamicModelMultipleChoiceField(
        queryset=NetAppSVM.objects.all(),
        required=False,
        label='SVM'
    )
    tenant_id = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        label='Tenant'
    )


class LUNFilterForm(NetBoxModelFilterSetForm):
    model = NetAppLUN
    tenant = DynamicModelMultipleChoiceField(queryset=Tenant.objects.all(), required=False)
    volume = DynamicModelMultipleChoiceField(queryset=NetAppVolume.objects.all(), required=False)
    qtree = DynamicModelMultipleChoiceField(queryset=NetAppQTree.objects.all(), required=False)
    name = forms.CharField(required=False)
    wwn = forms.CharField(required=False, label="WWN")
    os_type = forms.ChoiceField(required=False, choices=[("", "---------")] + list(NetAppLUN.OS_TYPE_CHOICES))
    uuid = forms.CharField(required=False, label="ONTAP LUN UUID")
    svm_id = DynamicModelMultipleChoiceField(
        queryset=NetAppSVM.objects.all(),
        required=False,
        label='SVM'
    )


#
# CSV forms
#

class ClusterCSVForm(NetBoxModelImportForm):
    class Meta:
        model = NetAppCluster
        fields = ("name", "ontap_version", "uuid", "description")


class NodeCSVForm(NetBoxModelImportForm):
    cluster = CSVModelChoiceField(queryset=NetAppCluster.objects.all(), to_field_name="name")
    device = CSVModelChoiceField(queryset=Device.objects.all(), to_field_name="name", required=False)

    class Meta:
        model = NetAppNode
        fields = ("name", "cluster", "device", "model", "serial_number", "uuid", "description")


class AggregateCSVForm(NetBoxModelImportForm):
    node = CSVModelChoiceField(queryset=NetAppNode.objects.all(), to_field_name="name")

    class Meta:
        model = NetAppAggregate
        fields = ("name", "node", "size", "uuid", "description")


class SVMCSVForm(NetBoxModelImportForm):
    cluster = CSVModelChoiceField(queryset=NetAppCluster.objects.all(), to_field_name="name", required=False)
    tenant = CSVModelChoiceField(queryset=Tenant.objects.all(), to_field_name="name", required=False)

    class Meta:
        model = NetAppSVM
        fields = ("name", "cluster", "tenant", "uuid", "description")


class VolumeCSVForm(NetBoxModelImportForm):
    svm = CSVModelChoiceField(queryset=NetAppSVM.objects.all(), to_field_name="name")
    aggregate = CSVModelChoiceField(queryset=NetAppAggregate.objects.all(), to_field_name="name")
    tenant = CSVModelChoiceField(queryset=Tenant.objects.all(), to_field_name="name", required=False)

    class Meta:
        model = NetAppVolume
        fields = ("name", "svm", "aggregate", "size", "tenant", "uuid", "description")


class QTreeCSVForm(NetBoxModelImportForm):
    volume = CSVModelChoiceField(queryset=NetAppVolume.objects.all(), to_field_name="name")

    class Meta:
        model = NetAppQTree
        fields = ("name", "volume", "description")


class QuotaCSVForm(NetBoxModelImportForm):
    volume = CSVModelChoiceField(queryset=NetAppVolume.objects.all(), to_field_name="name")
    qtree = CSVModelChoiceField(queryset=NetAppQTree.objects.all(), to_field_name="name", required=False)

    class Meta:
        model = NetAppQuota
        fields = (
            "volume",
            "qtree",
            "space_hard_limit",
            "space_soft_limit",
            "files_hard_limit",
            "files_soft_limit",
            "index",
            "description",
        )


class LUNCSVForm(NetBoxModelImportForm):
    volume = CSVModelChoiceField(queryset=NetAppVolume.objects.all(), to_field_name="name")
    qtree = CSVModelChoiceField(queryset=NetAppQTree.objects.all(), to_field_name="name", required=False)

    class Meta:
        model = NetAppLUN
        fields = ("name", "volume", "qtree", "size", "os_type", "wwn", "uuid", "description")
