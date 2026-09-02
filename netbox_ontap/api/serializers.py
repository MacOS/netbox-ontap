from rest_framework import serializers

from dcim.api.serializers import DeviceSerializer
from ipam.api.serializers import IPAddressSerializer
from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers import TenantSerializer

from ..models import (
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


class NetAppClusterSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_ontap-api:netappcluster-detail")
    management_ip = IPAddressSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = NetAppCluster
        fields = (
            "id",
            "url",
            "display",
            "name",
            "management_ip",
            "ontap_version",
            "uuid",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "uuid")


class NetAppNodeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_ontap-api:netappnode-detail")
    cluster = NetAppClusterSerializer(nested=True)
    device = DeviceSerializer(nested=True, required=False, allow_null=True)
    management_ip = IPAddressSerializer(nested=True, required=False, allow_null=True)
    ha_partner = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = NetAppNode
        fields = (
            "id",
            "url",
            "display",
            "name",
            "cluster",
            "device",
            "model",
            "serial_number",
            "management_ip",
            "uuid",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
            "ha_partner",
        )
        brief_fields = ("id", "url", "display", "name", "cluster", "uuid")

    def get_ha_partner(self, obj):
        partner = obj.ha_partner
        if partner is None:
            return None
        return NetAppNodeSerializer(partner, nested=True, context=self.context).data


class NetAppHAPairSerializer(NetBoxModelSerializer):
    """Backend-only serializer; NetAppHAPair has no registered viewset or API route."""

    node_a = NetAppNodeSerializer(nested=True)
    node_b = NetAppNodeSerializer(nested=True)

    class Meta:
        model = NetAppHAPair
        fields = (
            "id",
            "display",
            "node_a",
            "node_b",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "display", "node_a", "node_b")


class NetAppAggregateSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_ontap-api:netappaggregate-detail")
    node = NetAppNodeSerializer(nested=True)

    class Meta:
        model = NetAppAggregate
        fields = (
            "id",
            "url",
            "display",
            "name",
            "node",
            "size",
            "uuid",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "node", "size")


class NetAppSVMSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_ontap-api:netappsvm-detail")
    cluster = NetAppClusterSerializer(nested=True, required=False, allow_null=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    # The `tenant` field above only handles writes (an explicit override); reads always
    # show this object's resolved Tenant instead, so a single field never shows two values.
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        tenant = instance.get_tenant()
        ret['tenant'] = TenantSerializer(tenant, nested=True, context=self.context).data if tenant else None
        return ret

    class Meta:
        model = NetAppSVM
        fields = (
            "id",
            "url",
            "display",
            "name",
            "cluster",
            "tenant",
            "uuid",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "cluster", "tenant", "uuid")


class NetAppVolumeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_ontap-api:netappvolume-detail")
    svm = NetAppSVMSerializer(nested=True)
    aggregate = NetAppAggregateSerializer(nested=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        tenant = instance.get_tenant()
        ret['tenant'] = TenantSerializer(tenant, nested=True, context=self.context).data if tenant else None
        return ret

    class Meta:
        model = NetAppVolume
        fields = (
            "id",
            "url",
            "display",
            "name",
            "svm",
            "aggregate",
            "size",
            "tenant",
            "uuid",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "svm", "aggregate", "tenant", "uuid")


class NetAppQTreeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_ontap-api:netappqtree-detail")
    volume = NetAppVolumeSerializer(nested=True)
    tenant = serializers.SerializerMethodField(read_only=True)

    def get_tenant(self, obj):
        tenant = obj.get_tenant()
        return TenantSerializer(tenant, nested=True, context=self.context).data if tenant else None

    class Meta:
        model = NetAppQTree
        fields = (
            "id",
            "url",
            "display",
            "name",
            "volume",
            "tenant",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "volume")


class NetAppQuotaSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_ontap-api:netappquota-detail")
    volume = NetAppVolumeSerializer(nested=True)
    qtree = NetAppQTreeSerializer(nested=True, required=False, allow_null=True)
    tenant = serializers.SerializerMethodField(read_only=True)

    def get_tenant(self, obj):
        tenant = obj.get_tenant()
        return TenantSerializer(tenant, nested=True, context=self.context).data if tenant else None

    def validate(self, attrs):
        attrs = super().validate(attrs)

        volume = attrs.get("volume")
        qtree = attrs.get("qtree")

        if self.instance is not None:
            if volume is None:
                volume = self.instance.volume
            if qtree is None:
                qtree = self.instance.qtree

        if qtree is not None and volume is not None and qtree.volume_id != volume.pk:
            raise serializers.ValidationError(
                {
                    "qtree": "QTree must belong to the selected Volume.",
                }
            )

        return attrs

    class Meta:
        model = NetAppQuota
        fields = (
            "id",
            "url",
            "display",
            "volume",
            "qtree",
            "space_hard_limit",
            "space_soft_limit",
            "files_hard_limit",
            "files_soft_limit",
            "index",
            "tenant",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "volume", "qtree", "space_hard_limit", "index")


class NetAppLUNSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_ontap-api:netapplun-detail")
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)
    volume = NetAppVolumeSerializer(nested=True)
    qtree = NetAppQTreeSerializer(nested=True, required=False, allow_null=True)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        tenant = instance.get_tenant()
        ret['tenant'] = TenantSerializer(tenant, nested=True, context=self.context).data if tenant else None
        return ret

    class Meta:
        model = NetAppLUN
        fields = (
            "id",
            "url",
            "display",
            "name",
            "size",
            "os_type",
            "tenant",
            "volume",
            "qtree",
            "wwn",
            "uuid",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "size", "tenant", "volume", "qtree", "uuid")
