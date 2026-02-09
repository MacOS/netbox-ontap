from rest_framework import serializers

from virtualization.api.serializers import ClusterSerializer, VirtualMachineSerializer
from dcim.api.serializers import DeviceSerializer
from tenancy.api.serializers import TenantSerializer
from netbox.api.serializers import NetBoxModelSerializer
from netbox.api.fields import SerializedPKRelatedField
from ..models import StoragePool, LUN, Quota, StorageSession, Datastore, VMDK


class StoragePoolSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_storage-api:storagepool-detail'
    )
    device = DeviceSerializer(nested=True)

    class Meta:
        model = StoragePool
        fields = (
            'id', 'url', 'display', 'name', 'size', 'device', 'description',
            'tags', 'custom_fields', 'created', 'last_updated',
        )
        brief_fields = (
            'id', 'url', 'display', 'name', 'size', 'device',
        )


class LUNSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_storage-api:lun-detail'
    )
    storage_pool = StoragePoolSerializer(nested=True, required=False)
    tenant = TenantSerializer(nested=True, required=False)

    class Meta:
        model = LUN
        fields = (
            'id', 'url', 'display', 'name', 'size', 'storage_pool', 'wwn', 'svm_name',
            'tenant', 'description', 'tags', 'custom_fields',
            'created', 'last_updated', 
        )
        brief_fields = (
            'id', 'url', 'display', 'name', 'size', 'storage_pool', 'svm_name', 'tenant',
        )


class QuotaSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_storage-api:quota-detail'
    )
    tenant = TenantSerializer(nested=True, allow_null=True)

    class Meta:
        model = Quota
        fields = (
            'id', 'url', 'display', 'volume_name', 'size', 'tenant', 'qtree_name', 'svm_name', 'description',
            'tags', 'custom_fields', 'created', 'last_updated',
        )
        brief_fields = (
            'id', 'url', 'display', 'volume_name', 'size', 'tenant',
        )


class DatastoreSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_storage-api:datastore-detail'
    )
    lun = SerializedPKRelatedField(
        queryset=LUN.objects.all(),
        serializer=LUNSerializer,
        many=True
    )

    class Meta:
        model = Datastore
        fields = (
            'id', 'url', 'display', 'name', 'lun',
            'description', 'tags', 'custom_fields', 'created', 'last_updated',
        )
        brief_fields = (
            'id', 'url', 'display', 'name', 'lun',
        )


class StorageSessionSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_storage-api:storagesession-detail'
    )
    cluster = ClusterSerializer(nested=True)
    datastores = SerializedPKRelatedField(
        queryset=Datastore.objects.all(),
        serializer=DatastoreSerializer,
        many=True
    )

    class Meta:
        model = StorageSession
        fields = (
            'id', 'url', 'display', 'name', 'cluster', 'datastores',
            'description', 'tags', 'custom_fields', 'created', 'last_updated',
        )
        brief_fields = (
            'id', 'url', 'display', 'name', 'cluster', 'datastores',
        )


class VMDKSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='plugins-api:netbox_storage-api:vmdk-detail'
    )
    datastore = DatastoreSerializer(nested=True)
    vm = VirtualMachineSerializer(nested=True)

    class Meta:
        model = VMDK
        fields = (
            'id', 'url', 'display', 'vm', 'name', 'datastore',
            'size', 'tags', 'custom_fields', 'created', 'last_updated',
        )
        brief_fields = (
            'id', 'url', 'display', 'vm', 'name', 'datastore', 'size',
        )
