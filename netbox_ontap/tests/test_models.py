# SPDX-FileCopyrightText: Leonhard Kreißig (Deutsche Telekom AG) <leonhard.kreissig@telekom.de>
#
# SPDX-License-Identifier: Apache-2.0

from django.core.exceptions import ValidationError
from django.test import TestCase

from tenancy.models import Tenant

from netbox_ontap.models import (
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


class ClusterTestCase(TestCase):

    def test_uuid_must_be_unique_when_set(self):
        NetAppCluster.objects.create(name='Cluster 1', uuid='11111111-1111-1111-1111-111111111111')
        duplicate = NetAppCluster(name='Cluster 2', uuid='11111111-1111-1111-1111-111111111111')
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_multiple_null_uuids_are_allowed(self):
        NetAppCluster.objects.create(name='Cluster 1')
        cluster2 = NetAppCluster(name='Cluster 2')
        cluster2.full_clean()
        cluster2.save()
        self.assertEqual(NetAppCluster.objects.filter(uuid__isnull=True).count(), 2)

    def test_blank_uuid_is_normalized_when_saved_without_validation(self):
        cluster = NetAppCluster.objects.create(name='Cluster 1', uuid='')
        cluster.refresh_from_db()
        self.assertIsNone(cluster.uuid)


class NodeTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.cluster = NetAppCluster.objects.create(name='Cluster 1')

    def test_name_must_be_unique_within_cluster(self):
        NetAppNode.objects.create(name='Node 1', cluster=self.cluster)
        duplicate = NetAppNode(name='Node 1', cluster=self.cluster)
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_same_name_allowed_in_different_clusters(self):
        other_cluster = NetAppCluster.objects.create(name='Cluster 2')
        NetAppNode.objects.create(name='Node 1', cluster=self.cluster)
        node2 = NetAppNode(name='Node 1', cluster=other_cluster)
        node2.full_clean()

    def test_uuid_must_be_unique_when_set(self):
        NetAppNode.objects.create(name='Node 1', cluster=self.cluster, uuid='11111111-1111-1111-1111-111111111112')
        duplicate = NetAppNode(
            name='Node 2', cluster=self.cluster, uuid='11111111-1111-1111-1111-111111111112'
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()


class HAPairTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.cluster_a = NetAppCluster.objects.create(name='Cluster A')
        cls.cluster_b = NetAppCluster.objects.create(name='Cluster B')
        cls.node_a1 = NetAppNode.objects.create(name='Node A1', cluster=cls.cluster_a)
        cls.node_a2 = NetAppNode.objects.create(name='Node A2', cluster=cls.cluster_a)
        cls.node_b1 = NetAppNode.objects.create(name='Node B1', cluster=cls.cluster_b)

    def test_pair_within_same_cluster_is_valid(self):
        pair = NetAppHAPair(node_a=self.node_a1, node_b=self.node_a2)
        pair.full_clean()

    def test_pair_across_clusters_is_rejected(self):
        pair = NetAppHAPair(node_a=self.node_a1, node_b=self.node_b1)
        with self.assertRaises(ValidationError):
            pair.full_clean()

    def test_pair_with_same_node_twice_is_rejected(self):
        pair = NetAppHAPair(node_a=self.node_a1, node_b=self.node_a1)
        with self.assertRaises(ValidationError):
            pair.full_clean()

    def test_ha_pair_property_returns_pair_for_node_a(self):
        pair = NetAppHAPair.objects.create(node_a=self.node_a1, node_b=self.node_a2)
        self.assertEqual(self.node_a1.ha_pair, pair)
        pair.delete()

    def test_ha_pair_property_returns_pair_for_node_b(self):
        pair = NetAppHAPair.objects.create(node_a=self.node_a1, node_b=self.node_a2)
        self.assertEqual(self.node_a2.ha_pair, pair)
        pair.delete()

    def test_ha_partner_property_returns_peer(self):
        pair = NetAppHAPair.objects.create(node_a=self.node_a1, node_b=self.node_a2)
        self.assertEqual(self.node_a1.ha_partner, self.node_a2)
        self.assertEqual(self.node_a2.ha_partner, self.node_a1)
        pair.delete()

    def test_ha_pair_and_partner_are_none_when_unpaired(self):
        self.assertIsNone(self.node_a1.ha_pair)
        self.assertIsNone(self.node_a1.ha_partner)

    def test_ha_pair_is_private_backend_model(self):
        self.assertTrue(NetAppHAPair._netbox_private)

    def test_ha_pair_has_no_description_field(self):
        self.assertFalse(hasattr(NetAppHAPair(), 'description'))

    def test_ha_pair_has_no_tags_manager(self):
        self.assertFalse(hasattr(NetAppHAPair(), 'tags'))

    def test_ha_pair_has_change_logging_fields(self):
        pair = NetAppHAPair.objects.create(node_a=self.node_a1, node_b=self.node_a2)
        self.assertIsNotNone(pair.created)
        self.assertIsNotNone(pair.last_updated)
        pair.delete()


class AggregateTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.cluster = NetAppCluster.objects.create(name='Cluster 1')
        cls.node = NetAppNode.objects.create(name='Node 1', cluster=cls.cluster)

    def test_name_must_be_unique_within_node(self):
        NetAppAggregate.objects.create(name='Aggr 1', node=self.node)
        duplicate = NetAppAggregate(name='Aggr 1', node=self.node)
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_same_name_allowed_on_different_nodes(self):
        other_node = NetAppNode.objects.create(name='Node 2', cluster=self.cluster)
        NetAppAggregate.objects.create(name='Aggr 1', node=self.node)
        aggregate2 = NetAppAggregate(name='Aggr 1', node=other_node)
        aggregate2.full_clean()

    def test_uuid_must_be_unique_when_set(self):
        NetAppAggregate.objects.create(name='Aggr 1', node=self.node, uuid='22222222-2222-2222-2222-222222222222')
        duplicate = NetAppAggregate(
            name='Aggr 2', node=self.node, uuid='22222222-2222-2222-2222-222222222222'
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()


class VolumeAggregateClusterTestCase(TestCase):
    """The Aggregate's Node must belong to the same Cluster as the Volume's SVM."""

    @classmethod
    def setUpTestData(cls):
        cls.cluster_a = NetAppCluster.objects.create(name='Cluster A')
        cls.cluster_b = NetAppCluster.objects.create(name='Cluster B')
        cls.node_a = NetAppNode.objects.create(name='Node A', cluster=cls.cluster_a)
        cls.node_b = NetAppNode.objects.create(name='Node B', cluster=cls.cluster_b)
        cls.aggregate_a = NetAppAggregate.objects.create(name='Aggr A', node=cls.node_a)
        cls.aggregate_b = NetAppAggregate.objects.create(name='Aggr B', node=cls.node_b)
        cls.svm = NetAppSVM.objects.create(name='SVM 1', cluster=cls.cluster_a)

    def test_volume_with_matching_cluster_is_valid(self):
        volume = NetAppVolume(name='Vol 1', svm=self.svm, aggregate=self.aggregate_a)
        volume.full_clean()

    def test_volume_with_mismatched_cluster_is_rejected(self):
        volume = NetAppVolume(name='Vol 1', svm=self.svm, aggregate=self.aggregate_b)
        with self.assertRaises(ValidationError):
            volume.full_clean()

    def test_volume_name_must_be_unique_within_svm(self):
        NetAppVolume.objects.create(name='Vol 1', svm=self.svm, aggregate=self.aggregate_a)
        duplicate = NetAppVolume(name='Vol 1', svm=self.svm, aggregate=self.aggregate_a)
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_same_volume_name_allowed_under_different_svm(self):
        other_svm = NetAppSVM.objects.create(name='SVM 2', cluster=self.cluster_a)
        NetAppVolume.objects.create(name='Vol 1', svm=self.svm, aggregate=self.aggregate_a)
        volume2 = NetAppVolume(name='Vol 1', svm=other_svm, aggregate=self.aggregate_a)
        volume2.full_clean()

    def test_volume_uuid_must_be_unique_when_set(self):
        NetAppVolume.objects.create(
            name='Vol 1', svm=self.svm, aggregate=self.aggregate_a, uuid='33333333-3333-3333-3333-333333333333'
        )
        duplicate = NetAppVolume(
            name='Vol 2', svm=self.svm, aggregate=self.aggregate_a, uuid='33333333-3333-3333-3333-333333333333'
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()


class QTreeQuotaConsistencyTestCase(TestCase):
    """QTree names must be unique per Volume; Quota/LUN qtree assignments must belong to the selected Volume."""

    @classmethod
    def setUpTestData(cls):
        cls.cluster = NetAppCluster.objects.create(name='Cluster 1')
        cls.node = NetAppNode.objects.create(name='Node 1', cluster=cls.cluster)
        cls.aggregate = NetAppAggregate.objects.create(name='Aggr 1', node=cls.node)
        cls.svm = NetAppSVM.objects.create(name='SVM 1', cluster=cls.cluster)
        cls.volume_a = NetAppVolume.objects.create(name='Vol A', svm=cls.svm, aggregate=cls.aggregate)
        cls.volume_b = NetAppVolume.objects.create(name='Vol B', svm=cls.svm, aggregate=cls.aggregate)
        cls.qtree_a = NetAppQTree.objects.create(name='QTree A', volume=cls.volume_a)

    def test_qtree_name_must_be_unique_within_volume(self):
        duplicate = NetAppQTree(name='QTree A', volume=self.volume_a)
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_same_qtree_name_allowed_under_different_volume(self):
        qtree2 = NetAppQTree(name='QTree A', volume=self.volume_b)
        qtree2.full_clean()

    def test_quota_with_matching_volume_is_valid(self):
        quota = NetAppQuota(volume=self.volume_a, qtree=self.qtree_a, index='0')
        quota.full_clean()

    def test_quota_with_mismatched_volume_is_rejected(self):
        quota = NetAppQuota(volume=self.volume_b, qtree=self.qtree_a, index='0')
        with self.assertRaises(ValidationError):
            quota.full_clean()

    def test_lun_with_mismatched_qtree_volume_is_rejected(self):
        lun = NetAppLUN(name='LUN 1', volume=self.volume_b, qtree=self.qtree_a, size=100)
        with self.assertRaises(ValidationError):
            lun.full_clean()

    def test_lun_with_matching_qtree_volume_is_valid(self):
        lun = NetAppLUN(name='LUN 1', volume=self.volume_a, qtree=self.qtree_a, size=100)
        lun.full_clean()


class TenantResolutionTestCase(TestCase):
    """Every object must expose exactly one effective Tenant - its own, or the nearest ancestor's."""

    @classmethod
    def setUpTestData(cls):
        cls.tenant_a = Tenant.objects.create(name='Tenant A', slug='tenant-a')
        cls.tenant_b = Tenant.objects.create(name='Tenant B', slug='tenant-b')
        cls.cluster = NetAppCluster.objects.create(name='Cluster 1')
        cls.node = NetAppNode.objects.create(name='Node 1', cluster=cls.cluster)
        cls.aggregate = NetAppAggregate.objects.create(name='Aggr 1', node=cls.node)

    def test_svm_without_tenant_resolves_to_none(self):
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=self.cluster)
        self.assertIsNone(svm.get_tenant())

    def test_volume_inherits_tenant_from_svm(self):
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=self.cluster, tenant=self.tenant_a)
        volume = NetAppVolume.objects.create(name='Vol 1', svm=svm, aggregate=self.aggregate)
        self.assertIsNone(volume.tenant_id)
        self.assertEqual(volume.get_tenant(), self.tenant_a)

    def test_lun_inherits_tenant_through_volume_and_svm(self):
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=self.cluster, tenant=self.tenant_a)
        volume = NetAppVolume.objects.create(name='Vol 1', svm=svm, aggregate=self.aggregate)
        lun = NetAppLUN.objects.create(name='LUN 1', volume=volume, size=100)
        self.assertIsNone(lun.tenant_id)
        self.assertEqual(lun.get_tenant(), self.tenant_a)

    def test_qtree_and_quota_mirror_volume_tenant(self):
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=self.cluster, tenant=self.tenant_a)
        volume = NetAppVolume.objects.create(name='Vol 1', svm=svm, aggregate=self.aggregate)
        qtree = NetAppQTree.objects.create(name='QTree 1', volume=volume)
        quota = NetAppQuota.objects.create(volume=volume, index='0')
        self.assertEqual(qtree.get_tenant(), self.tenant_a)
        self.assertEqual(quota.get_tenant(), self.tenant_a)
        self.assertEqual(qtree.tenant, self.tenant_a)
        self.assertEqual(quota.tenant, self.tenant_a)

    def test_explicit_tenant_matching_parent_is_allowed(self):
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=self.cluster, tenant=self.tenant_a)
        volume = NetAppVolume(
            name='Vol 1', svm=svm, aggregate=self.aggregate, tenant=self.tenant_a
        )
        volume.full_clean()
        self.assertEqual(volume.get_tenant(), self.tenant_a)

    def test_explicit_tenant_differing_from_tenanted_parent_is_rejected(self):
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=self.cluster, tenant=self.tenant_a)
        volume = NetAppVolume(
            name='Vol 1', svm=svm, aggregate=self.aggregate, tenant=self.tenant_b
        )
        with self.assertRaises(ValidationError):
            volume.full_clean()

    def test_explicit_tenant_differing_from_tenanted_grandparent_is_rejected(self):
        """The upward check must resolve through an untenanted intermediate Volume."""
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=self.cluster, tenant=self.tenant_a)
        volume = NetAppVolume.objects.create(name='Vol 1', svm=svm, aggregate=self.aggregate)
        lun = NetAppLUN(name='LUN 1', volume=volume, size=100, tenant=self.tenant_b)
        with self.assertRaises(ValidationError):
            lun.full_clean()

    def test_explicit_tenant_is_allowed_when_parent_has_none(self):
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=self.cluster)
        volume = NetAppVolume(
            name='Vol 1', svm=svm, aggregate=self.aggregate, tenant=self.tenant_a
        )
        volume.full_clean()
        self.assertEqual(volume.get_tenant(), self.tenant_a)


class TenantOrderingTestCase(TestCase):
    """Tenant-related outcomes must not depend on the order objects/assignments are created in."""

    @classmethod
    def setUpTestData(cls):
        cls.tenant_a = Tenant.objects.create(name='Tenant A', slug='tenant-a')
        cls.tenant_b = Tenant.objects.create(name='Tenant B', slug='tenant-b')
        cls.cluster = NetAppCluster.objects.create(name='Cluster 1')
        cls.node = NetAppNode.objects.create(name='Node 1', cluster=cls.cluster)
        cls.aggregate = NetAppAggregate.objects.create(name='Aggr 1', node=cls.node)

    def test_tenant_assigned_before_children_are_created(self):
        """Parent Tenant set first: children created afterwards must inherit immediately."""
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=self.cluster, tenant=self.tenant_a)
        volume = NetAppVolume.objects.create(name='Vol 1', svm=svm, aggregate=self.aggregate)
        lun = NetAppLUN.objects.create(name='LUN 1', volume=volume, size=100)
        self.assertEqual(volume.get_tenant(), self.tenant_a)
        self.assertEqual(lun.get_tenant(), self.tenant_a)

    def test_tenant_assigned_after_children_already_exist(self):
        """Children created first while the parent is untenanted; the parent later adopts the
        same Tenant a descendant already explicitly holds - must be allowed and stay consistent."""
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=self.cluster)
        volume = NetAppVolume.objects.create(name='Vol 1', svm=svm, aggregate=self.aggregate)
        lun = NetAppLUN.objects.create(name='LUN 1', volume=volume, size=100, tenant=self.tenant_a)

        svm.tenant = self.tenant_a
        svm.full_clean()
        svm.save()

        self.assertEqual(svm.get_tenant(), self.tenant_a)
        self.assertEqual(volume.get_tenant(), self.tenant_a)
        lun.refresh_from_db()
        self.assertEqual(lun.get_tenant(), self.tenant_a)

    def test_tenant_assigned_after_children_exist_with_conflicting_tenant_is_rejected(self):
        """Children created first with an explicit Tenant; the parent then tries to adopt a
        DIFFERENT Tenant - must be rejected regardless of creation order."""
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=self.cluster)
        volume = NetAppVolume.objects.create(name='Vol 1', svm=svm, aggregate=self.aggregate)
        NetAppLUN.objects.create(name='LUN 1', volume=volume, size=100, tenant=self.tenant_b)

        svm.tenant = self.tenant_a
        with self.assertRaises(ValidationError):
            svm.full_clean()

    def test_tenant_assigned_after_deep_conflicting_descendant_through_empty_intermediate(self):
        """Same as above, but the conflicting Tenant sits two levels down, through a Volume that
        itself has no explicit Tenant - the check must still recurse through it."""
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=self.cluster)
        volume = NetAppVolume.objects.create(name='Vol 1', svm=svm, aggregate=self.aggregate)
        NetAppLUN.objects.create(name='LUN 1', volume=volume, size=100, tenant=self.tenant_b)

        svm.tenant = self.tenant_a
        with self.assertRaises(ValidationError):
            svm.full_clean()

        svm.tenant = self.tenant_b
        svm.full_clean()
        svm.save()
        self.assertEqual(svm.get_tenant(), self.tenant_b)

    def test_tenant_cleared_on_parent_is_reflected_immediately_on_read(self):
        """Clearing a parent's Tenant must be reflected immediately when reading a purely
        inheriting descendant's resolved Tenant, since nothing is cached on the child."""
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=self.cluster, tenant=self.tenant_a)
        volume = NetAppVolume.objects.create(name='Vol 1', svm=svm, aggregate=self.aggregate)
        self.assertEqual(volume.get_tenant(), self.tenant_a)

        svm.tenant = None
        svm.full_clean()
        svm.save()

        self.assertIsNone(volume.get_tenant())


class DescendantTenantsTestCase(TestCase):
    """get_descendant_tenants() must recurse through every level, including empty intermediates."""

    @classmethod
    def setUpTestData(cls):
        cls.tenant_a = Tenant.objects.create(name='Tenant A', slug='tenant-a')
        cls.tenant_b = Tenant.objects.create(name='Tenant B', slug='tenant-b')
        cls.cluster = NetAppCluster.objects.create(name='Cluster 1')
        cls.node = NetAppNode.objects.create(name='Node 1', cluster=cls.cluster)
        cls.aggregate = NetAppAggregate.objects.create(name='Aggr 1', node=cls.node)

    def test_empty_when_svm_is_untenanted_and_has_no_children(self):
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=self.cluster)
        self.assertEqual(list(svm.get_descendant_tenants()), [])

    def test_finds_tenant_on_direct_child_volume(self):
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=self.cluster)
        NetAppVolume.objects.create(
            name='Vol 1', svm=svm, aggregate=self.aggregate, tenant=self.tenant_a
        )
        self.assertEqual(set(svm.get_descendant_tenants()), {self.tenant_a})

    def test_finds_tenant_through_empty_intermediate_volume(self):
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=self.cluster)
        volume = NetAppVolume.objects.create(name='Vol 1', svm=svm, aggregate=self.aggregate)
        NetAppLUN.objects.create(name='LUN 1', volume=volume, size=100, tenant=self.tenant_b)
        self.assertEqual(set(svm.get_descendant_tenants()), {self.tenant_b})

    def test_is_trivially_empty_once_svm_itself_has_a_tenant(self):
        """Once the SVM has a Tenant, no descendant can diverge (enforced by validation),
        so there is nothing left to surface here."""
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=self.cluster, tenant=self.tenant_a)
        NetAppVolume.objects.create(name='Vol 1', svm=svm, aggregate=self.aggregate)
        self.assertEqual(list(svm.get_descendant_tenants()), [])


class TenantQuerySetAggregationTestCase(TestCase):
    """for_tenant() must include directly- and inherited-tenant objects, and exclude other tenants'."""

    @classmethod
    def setUpTestData(cls):
        cls.tenant_a = Tenant.objects.create(name='Tenant A', slug='tenant-a')
        cls.tenant_b = Tenant.objects.create(name='Tenant B', slug='tenant-b')
        cls.cluster = NetAppCluster.objects.create(name='Cluster 1')
        cls.node = NetAppNode.objects.create(name='Node 1', cluster=cls.cluster)
        cls.aggregate = NetAppAggregate.objects.create(name='Aggr 1', node=cls.node)

    def test_for_tenant_includes_direct_and_inherited_volumes_only(self):
        svm_a = NetAppSVM.objects.create(name='SVM A', cluster=self.cluster, tenant=self.tenant_a)
        vol_inherited = NetAppVolume.objects.create(name='Vol Inherited', svm=svm_a, aggregate=self.aggregate)

        svm_bare = NetAppSVM.objects.create(name='SVM Bare', cluster=self.cluster)
        vol_explicit = NetAppVolume.objects.create(
            name='Vol Explicit', svm=svm_bare, aggregate=self.aggregate, tenant=self.tenant_a
        )

        svm_b = NetAppSVM.objects.create(name='SVM B', cluster=self.cluster, tenant=self.tenant_b)
        NetAppVolume.objects.create(name='Vol Other', svm=svm_b, aggregate=self.aggregate)

        result = set(NetAppVolume.objects.for_tenant(self.tenant_a))
        self.assertEqual(result, {vol_inherited, vol_explicit})

    def test_for_tenant_lun_resolves_through_volume_and_svm(self):
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=self.cluster, tenant=self.tenant_a)
        volume = NetAppVolume.objects.create(name='Vol 1', svm=svm, aggregate=self.aggregate)
        lun_inherited = NetAppLUN.objects.create(name='LUN Inherited', volume=volume, size=1)

        other_svm = NetAppSVM.objects.create(name='SVM Other', cluster=self.cluster)
        other_volume = NetAppVolume.objects.create(name='Vol Other', svm=other_svm, aggregate=self.aggregate)
        lun_explicit = NetAppLUN.objects.create(
            name='LUN Explicit', volume=other_volume, size=1, tenant=self.tenant_a
        )
        NetAppLUN.objects.create(name='LUN Unrelated', volume=other_volume, size=1)

        result = set(NetAppLUN.objects.for_tenant(self.tenant_a))
        self.assertEqual(result, {lun_inherited, lun_explicit})
