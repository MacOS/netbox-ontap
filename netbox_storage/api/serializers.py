from rest_framework import serializers

from netbox.api.serializers import NetBoxModelSerializer
from tenancy.models import Tenant
from tenancy.api.serializers import TenantSerializer
from virtualization.models import Cluster
from virtualization.api.serializers import ClusterSerializer

from ..models import LUN, QTree, Quota, SVM, Volume


class SVMSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:ontap-api:svm-detail")
    cluster = ClusterSerializer(nested=True, read_only=True)
    tenant = TenantSerializer(nested=True, required=False, allow_null=True, read_only=True)

    cluster_id = serializers.PrimaryKeyRelatedField(source="cluster", queryset=Cluster.objects.all(), write_only=True)
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
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:ontap-api:volume-detail")
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
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:ontap-api:qtree-detail")
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
            "uuid",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "volume", "uuid")


class QuotaSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:ontap-api:quota-detail")
    qtree = QTreeSerializer(nested=True, required=False, allow_null=True, read_only=True)

    qtree_id = serializers.PrimaryKeyRelatedField(
        source="qtree", queryset=QTree.objects.all(), write_only=True, required=False, allow_null=True
    )
    qtree_uuid = serializers.SlugRelatedField(
        source="qtree",
        queryset=QTree.objects.exclude(uuid__isnull=True),
        slug_field="uuid",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Quota
        fields = (
            "id",
            "url",
            "display",
            "qtree",
            "qtree_id",
            "qtree_uuid",
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
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:ontap-api:lun-detail")
    tenant = TenantSerializer(nested=True, required=False, allow_null=True, read_only=True)
    svm = SVMSerializer(nested=True, required=False, allow_null=True, read_only=True)
    qtree = QTreeSerializer(nested=True, required=False, allow_null=True, read_only=True)

    tenant_id = serializers.PrimaryKeyRelatedField(
        source="tenant", queryset=Tenant.objects.all(), write_only=True, required=False, allow_null=True
    )
    svm_id = serializers.PrimaryKeyRelatedField(source="svm", queryset=SVM.objects.all(), write_only=True, required=False, allow_null=True)
    svm_uuid = serializers.SlugRelatedField(
        source="svm",
        queryset=SVM.objects.exclude(uuid__isnull=True),
        slug_field="uuid",
        write_only=True,
        required=False,
        allow_null=True,
    )
    qtree_id = serializers.PrimaryKeyRelatedField(
        source="qtree", queryset=QTree.objects.all(), write_only=True, required=False, allow_null=True
    )
    qtree_uuid = serializers.SlugRelatedField(
        source="qtree",
        queryset=QTree.objects.exclude(uuid__isnull=True),
        slug_field="uuid",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = LUN
        fields = (
            "id",
            "url",
            "display",
            "name",
            "size",
            "tenant",
            "tenant_id",
            "svm",
            "svm_id",
            "svm_uuid",
            "qtree",
            "qtree_id",
            "qtree_uuid",
            "wwn",
            "uuid",
            "description",
            "tags",
            "custom_fields",
            "created",
            "last_updated",
        )
        brief_fields = ("id", "url", "display", "name", "size", "tenant", "svm", "qtree", "uuid")
