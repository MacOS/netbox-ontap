from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.models import Tenant
from tenancy.api.serializers import TenantSerializer
from virtualization.models import Cluster
from virtualization.api.serializers import ClusterSerializer

from ..models import LUN, QTree, Quota, SVM, Volume


def _has_value(value):
    return value not in (None, "")


def _validate_id_uuid_match(initial_data, *, id_key, uuid_key, queryset, object_label):
    id_value = initial_data.get(id_key)
    uuid_value = initial_data.get(uuid_key)

    if not (_has_value(id_value) and _has_value(uuid_value)):
        return

    # Let field-level validation handle malformed values and missing objects.
    try:
        obj_by_id = queryset.get(pk=id_value)
        obj_by_uuid = queryset.get(uuid=uuid_value)
    except Exception:
        return

    if obj_by_id.pk != obj_by_uuid.pk:
        raise serializers.ValidationError(
            {
                id_key: f"{id_key} and {uuid_key} reference different {object_label} objects.",
                uuid_key: f"{id_key} and {uuid_key} reference different {object_label} objects.",
            }
        )


class SVMSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_ontap-api:svm-detail")
    cluster = ClusterSerializer(nested=True, read_only=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True, read_only=True)

    cluster_id = serializers.PrimaryKeyRelatedField(
        source="cluster",
        queryset=Cluster.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    tenant_id = serializers.PrimaryKeyRelatedField(
        source="tenant", queryset=Tenant.objects.all(), write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = SVM
        fields = (
            "id",
            "url",
            "display",
            "name",
            "cluster",
            "cluster_id",
            "tenant",
            "tenant_id",
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
    svm = SVMSerializer(nested=True, read_only=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True, read_only=True)

    svm_id = serializers.PrimaryKeyRelatedField(source="svm", queryset=SVM.objects.all(), write_only=True, required=False)
    svm_uuid = serializers.SlugRelatedField(
        source="svm",
        queryset=SVM.objects.exclude(uuid__isnull=True),
        slug_field="uuid",
        write_only=True,
        required=False,
    )
    tenant_id = serializers.PrimaryKeyRelatedField(
        source="tenant", queryset=Tenant.objects.all(), write_only=True, required=False, allow_null=True
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        initial_data = getattr(self, "initial_data", {})

        _validate_id_uuid_match(
            initial_data,
            id_key="svm_id",
            uuid_key="svm_uuid",
            queryset=SVM.objects.all(),
            object_label="SVM",
        )

        if self.instance is None and attrs.get("svm") is None:
            raise serializers.ValidationError(
                {
                    "svm_id": "One of svm_id or svm_uuid is required.",
                    "svm_uuid": "One of svm_id or svm_uuid is required.",
                }
            )

        return attrs

    class Meta:
        model = Volume
        fields = (
            "id",
            "url",
            "display",
            "name",
            "svm",
            "svm_id",
            "svm_uuid",
            "tenant",
            "tenant_id",
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
    volume = VolumeSerializer(nested=True, read_only=True)

    volume_id = serializers.PrimaryKeyRelatedField(
        source="volume", queryset=Volume.objects.all(), write_only=True, required=False
    )
    volume_uuid = serializers.SlugRelatedField(
        source="volume",
        queryset=Volume.objects.exclude(uuid__isnull=True),
        slug_field="uuid",
        write_only=True,
        required=False,
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        initial_data = getattr(self, "initial_data", {})

        _validate_id_uuid_match(
            initial_data,
            id_key="volume_id",
            uuid_key="volume_uuid",
            queryset=Volume.objects.all(),
            object_label="Volume",
        )

        if self.instance is None and attrs.get("volume") is None:
            raise serializers.ValidationError(
                {
                    "volume_id": "One of volume_id or volume_uuid is required.",
                    "volume_uuid": "One of volume_id or volume_uuid is required.",
                }
            )

        return attrs

    class Meta:
        model = QTree
        fields = (
            "id",
            "url",
            "display",
            "name",
            "volume",
            "volume_id",
            "volume_uuid",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "volume")


class QuotaSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_ontap-api:quota-detail")
    qtree = QTreeSerializer(nested=True, required=False, allow_null=True, read_only=True)

    qtree_id = serializers.PrimaryKeyRelatedField(
        source="qtree", queryset=QTree.objects.all(), write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = Quota
        fields = (
            "id",
            "url",
            "display",
            "qtree",
            "qtree_id",
            "size",
            "index",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "qtree", "size", "index")


class LUNSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_ontap-api:lun-detail")
    tenant = TenantSerializer(nested=True, required=False, allow_null=True, read_only=True)
    volume = VolumeSerializer(nested=True, read_only=True)
    qtree = QTreeSerializer(nested=True, required=False, allow_null=True, read_only=True)

    volume_id = serializers.PrimaryKeyRelatedField(
        source="volume",
        queryset=Volume.objects.all(),
        write_only=True,
        required=False,
    )
    volume_uuid = serializers.SlugRelatedField(
        source="volume",
        queryset=Volume.objects.exclude(uuid__isnull=True),
        slug_field="uuid",
        write_only=True,
        required=False,
    )
    qtree_id = serializers.PrimaryKeyRelatedField(
        source="qtree", queryset=QTree.objects.all(), write_only=True, required=False, allow_null=True
    )

    def validate(self, attrs):
        attrs = super().validate(attrs)
        initial_data = getattr(self, "initial_data", {})

        _validate_id_uuid_match(
            initial_data,
            id_key="volume_id",
            uuid_key="volume_uuid",
            queryset=Volume.objects.all(),
            object_label="Volume",
        )

        if self.instance is None and attrs.get("volume") is None:
            raise serializers.ValidationError(
                {
                    "volume_id": "One of volume_id or volume_uuid is required.",
                    "volume_uuid": "One of volume_id or volume_uuid is required.",
                }
            )

        return attrs

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
            "volume_id",
            "volume_uuid",
            "qtree",
            "qtree_id",
            "wwn",
            "uuid",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "size", "tenant", "volume", "qtree", "uuid")
