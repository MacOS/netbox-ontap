from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.api.serializers import TenantSerializer
from virtualization.api.serializers import ClusterSerializer

from ..models import LUN, QTree, Quota, SVM, Volume


class SVMSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_ontap-api:svm-detail")
    cluster = ClusterSerializer(nested=True, required=False, allow_null=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = SVM
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


class VolumeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_ontap-api:volume-detail")
    svm = SVMSerializer(nested=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = Volume
        fields = (
            "id",
            "url",
            "display",
            "name",
            "svm",
            "tenant",
            "uuid",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "svm", "tenant", "uuid")


class QTreeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_ontap-api:qtree-detail")
    volume = VolumeSerializer(nested=True)

    class Meta:
        model = QTree
        fields = (
            "id",
            "url",
            "display",
            "name",
            "volume",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "volume")


class QuotaSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_ontap-api:quota-detail")
    volume = VolumeSerializer(nested=True)
    qtree = QTreeSerializer(nested=True, required=False, allow_null=True)

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
        model = Quota
        fields = (
            "id",
            "url",
            "display",
            "volume",
            "qtree",
            "size",
            "index",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "volume", "qtree", "size", "index")


class LUNSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_ontap-api:lun-detail")
    tenant = TenantSerializer(nested=True, required=False, allow_null=True, read_only=True)
    volume = VolumeSerializer(nested=True)
    qtree = QTreeSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = LUN
        fields = (
            "id",
            "url",
            "display",
            "name",
            "size",
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
