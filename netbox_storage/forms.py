from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm, NetBoxModelImportForm
from utilities.forms.fields import DynamicModelChoiceField, CSVModelChoiceField, DynamicModelMultipleChoiceField, CSVModelMultipleChoiceField
from dcim.models import Device
from virtualization.models import Cluster, VirtualMachine
from tenancy.models import Tenant
from .models import StoragePool, StorageSession, LUN, Datastore, VMDK, Quota


#
# Regular forms
#

class StoragePoolForm(NetBoxModelForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all()
    )

    class Meta:
        model = StoragePool
        fields = ('name', 'size', 'device', 'description', 'tags')


class LUNForm(NetBoxModelForm):
    storage_pool = DynamicModelChoiceField(
        queryset=StoragePool.objects.all(),
        required=False
    )
    
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )

    class Meta:
        model = LUN
        fields = ('storage_pool', 'tenant','name', 'size', 'wwn', 'description')


class QuotaForm(NetBoxModelForm):
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )

    class Meta:
        model = Quota
        fields = ('volume_name', 'size', 'tenant', 'qtree_name', 'svm_name', 'description')



class DatastoreForm(NetBoxModelForm):
    lun = DynamicModelMultipleChoiceField(
        queryset=LUN.objects.all()
    )

    class Meta:
        model = LUN
        fields = ('lun', 'name', 'description')


class StorageSessionForm(NetBoxModelForm):
    cluster = DynamicModelChoiceField(
        queryset=Cluster.objects.all(),
    )
    datastores = DynamicModelMultipleChoiceField(
        queryset=Datastore.objects.all()
    )

    class Meta:
        model = StorageSession
        fields = (
            'name', 'cluster', 'datastores', 'description'
        )


class VMDKForm(NetBoxModelForm):
    vm = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        label='Virtual Machine'
    )
    datastore = DynamicModelChoiceField(
        queryset=Datastore.objects.all(),
        query_params={
            'reachable_by_vm': '$vm'
        }
    )

    class Meta:
        model = VMDK
        fields = (
            'vm', 'datastore', 'name', 'size',
        )


#
# Filter forms
#

class StoragePoolFilterForm(NetBoxModelFilterSetForm):
    model = StoragePool
    device = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False
    )
    name = forms.CharField(
        required=False
    )


class LUNFilterForm(NetBoxModelFilterSetForm):
    model = LUN
    storage_pool = DynamicModelMultipleChoiceField(
        queryset=StoragePool.objects.all(),
        required=False
    )
    tenant = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    name = forms.CharField(
        required=False
    )
    wwn = forms.CharField(
        required=False,
        label='WWN'
    )
    
        
class QuotaFilterForm(NetBoxModelFilterSetForm):
    model = Quota
    tenant = DynamicModelMultipleChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    volume_name = forms.CharField(
        required=False,
        label='Volume Name'
    )
    qtree_name = forms.CharField(
        required=False,
        label='Qtree Name'
    )
    svm_name = forms.CharField(
        required=False,
        label='SVM Name'
    )


class DatastoreFilterForm(NetBoxModelFilterSetForm):
    model = Datastore
    lun = DynamicModelMultipleChoiceField(
        queryset=LUN.objects.all(),
        required=False
    )
    name = forms.CharField(
        required=False
    )
    reachable_by_vm = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label='Reachable by these Virtual Machines'
    )


class StorageSessionFilterForm(NetBoxModelFilterSetForm):
    model = StorageSession
    cluster = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False
    )
    datastores = DynamicModelMultipleChoiceField(
        queryset=Datastore.objects.all(),
        required=False
    )
    name = forms.CharField(
        required=False
    )


class VMDKFilterForm(NetBoxModelFilterSetForm):
    model = VMDK
    datastore = DynamicModelMultipleChoiceField(
        queryset=Datastore.objects.all(),
        required=False
    )
    vm = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False
    )
    name = forms.CharField(
        required=False
    )


#
# CSV Forms
#

class StoragePoolCSVForm(NetBoxModelImportForm):
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
    )

    class Meta:
        model = StoragePool
        fields = ('name', 'size', 'device', 'description')


class LUNCSVForm(NetBoxModelImportForm):
    storage_pool = CSVModelChoiceField(
        queryset=StoragePool.objects.all(),
        to_field_name='name',
    )

    class Meta:
        model = LUN
        fields = ('storage_pool', 'name', 'size', 'wwn', 'description')

       
class QuotaCSVForm(NetBoxModelImportForm):
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='name',
        required=False
    )

    class Meta:
        model = Quota
        fields = ('volume_name', 'size', 'tenant', 'qtree_name', 'svm_name', 'description')


class DatastoreCSVForm(NetBoxModelImportForm):
    lun = CSVModelMultipleChoiceField(
        queryset=LUN.objects.all(),
        to_field_name='name',
        help_text='A single LUN name or multiple LUN names separated by commas ("LUN" or "LUN1,LUN2,LUN3")'
    )

    class Meta:
        model = Datastore
        fields = ('lun', 'name', 'description')


class StorageSessionCSVForm(NetBoxModelImportForm):
    cluster = CSVModelChoiceField(
        queryset=Cluster.objects.all(),
        to_field_name='name',
    )
    datastores = CSVModelMultipleChoiceField(
        queryset=Datastore.objects.all(),
        to_field_name='name',
        help_text='A single Datastore name or multiple Datastore names separated by commas ("datastore1" or "datastore1,datastore2,datastore3")'
    )

    class Meta:
        model = StorageSession
        fields = ('cluster', 'datastores', 'name', 'description')


class VMDKCSVForm(NetBoxModelImportForm):
    vm = CSVModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        to_field_name='name',
    )
    datastore = CSVModelChoiceField(
        queryset=Datastore.objects.all(),
        to_field_name='name',
    )

    class Meta:
        model = VMDK
        fields = ('vm', 'datastore', 'name', 'size')
