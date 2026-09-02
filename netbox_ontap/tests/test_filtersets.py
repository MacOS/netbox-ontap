from django.test import TestCase

from tenancy.models import Tenant

from netbox_ontap.filtersets import (
    AggregateFilterSet,
    ClusterFilterSet,
    LUNFilterSet,
    NodeFilterSet,
    QTreeFilterSet,
    QuotaFilterSet,
    SVMFilterSet,
    VolumeFilterSet,
)
from netbox_ontap.models import (
    NetAppAggregate,
    NetAppCluster,
    NetAppLUN,
    NetAppNode,
    NetAppQTree,
    NetAppQuota,
    NetAppSVM,
    NetAppVolume,
)


class ClusterFilterSetTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        NetAppCluster.objects.bulk_create([
            NetAppCluster(name='fs-cluster-1', uuid='11111111-1111-1111-1111-111111111101'),
            NetAppCluster(name='fs-cluster-2', uuid='11111111-1111-1111-1111-111111111102'),
        ])

    def _qs(self):
        return NetAppCluster.objects.filter(name__startswith='fs-cluster-')

    def test_search_by_name(self):
        fs = ClusterFilterSet({'q': 'fs-cluster-1'}, queryset=self._qs())
        self.assertEqual(fs.qs.count(), 1)

    def test_search_by_uuid(self):
        fs = ClusterFilterSet({'q': '111111111102'}, queryset=self._qs())
        self.assertEqual(fs.qs.count(), 1)

    def test_search_no_match(self):
        fs = ClusterFilterSet({'q': 'does-not-exist'}, queryset=self._qs())
        self.assertEqual(fs.qs.count(), 0)


class NodeFilterSetTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.cluster = NetAppCluster.objects.create(name='fs-node-cluster')
        NetAppNode.objects.bulk_create([
            NetAppNode(name='fs-node-1', cluster=cls.cluster, serial_number='SN-FS-1'),
            NetAppNode(name='fs-node-2', cluster=cls.cluster, serial_number='SN-FS-2'),
        ])

    def _qs(self):
        return NetAppNode.objects.filter(name__startswith='fs-node-')

    def test_search_by_name(self):
        fs = NodeFilterSet({'q': 'fs-node-1'}, queryset=self._qs())
        self.assertEqual(fs.qs.count(), 1)

    def test_search_by_serial_number(self):
        fs = NodeFilterSet({'q': 'SN-FS-2'}, queryset=self._qs())
        self.assertEqual(fs.qs.count(), 1)

    def test_filter_by_cluster_id(self):
        fs = NodeFilterSet({'cluster': [self.cluster.pk]}, queryset=self._qs())
        self.assertEqual(fs.qs.count(), 2)


class AggregateFilterSetTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cluster_a = NetAppCluster.objects.create(name='fs-aggr-cluster-a')
        cluster_b = NetAppCluster.objects.create(name='fs-aggr-cluster-b')
        node_a = NetAppNode.objects.create(name='fs-aggr-node-a', cluster=cluster_a)
        node_b = NetAppNode.objects.create(name='fs-aggr-node-b', cluster=cluster_b)
        cls.svm_a = NetAppSVM.objects.create(name='fs-aggr-svm-a', cluster=cluster_a)

        NetAppAggregate.objects.bulk_create([
            NetAppAggregate(name='fs-aggr-1', node=node_a),
            NetAppAggregate(name='fs-aggr-2', node=node_b),
        ])

    def _qs(self):
        return NetAppAggregate.objects.filter(name__startswith='fs-aggr-')

    def test_search_by_name(self):
        fs = AggregateFilterSet({'q': 'fs-aggr-1'}, queryset=self._qs())
        self.assertEqual(fs.qs.count(), 1)

    def test_filter_by_svm_matches_same_cluster_only(self):
        """SVM filter must only return Aggregates whose Node shares the SVM's Cluster."""
        fs = AggregateFilterSet({'svm': self.svm_a.pk}, queryset=self._qs())
        self.assertEqual(fs.qs.count(), 1)
        self.assertEqual(fs.qs.first().name, 'fs-aggr-1')


class SVMFilterSetTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.create(name='fs-svm-tenant', slug='fs-svm-tenant')
        cluster = NetAppCluster.objects.create(name='fs-svm-cluster')
        NetAppSVM.objects.bulk_create([
            NetAppSVM(name='fs-svm-1', cluster=cluster, tenant=cls.tenant),
            NetAppSVM(name='fs-svm-2', cluster=cluster),
        ])

    def _qs(self):
        return NetAppSVM.objects.filter(name__startswith='fs-svm-')

    def test_search_by_name(self):
        fs = SVMFilterSet({'q': 'fs-svm-1'}, queryset=self._qs())
        self.assertEqual(fs.qs.count(), 1)

    def test_filter_by_tenant_id(self):
        fs = SVMFilterSet({'tenant_id': [self.tenant.pk]}, queryset=self._qs())
        self.assertEqual(fs.qs.count(), 1)
        self.assertEqual(fs.qs.first().name, 'fs-svm-1')


class VolumeFilterSetTestCase(TestCase):
    """Tenant filtering must include both directly-tenanted and inherited Volumes."""

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.create(name='fs-vol-tenant', slug='fs-vol-tenant')
        cluster = NetAppCluster.objects.create(name='fs-vol-cluster')
        node = NetAppNode.objects.create(name='fs-vol-node', cluster=cluster)
        aggregate = NetAppAggregate.objects.create(name='fs-vol-aggr', node=node)

        svm_tenanted = NetAppSVM.objects.create(name='fs-vol-svm-tenanted', cluster=cluster, tenant=cls.tenant)
        svm_bare = NetAppSVM.objects.create(name='fs-vol-svm-bare', cluster=cluster)

        cls.vol_inherited = NetAppVolume.objects.create(
            name='fs-vol-inherited', svm=svm_tenanted, aggregate=aggregate
        )
        cls.vol_explicit = NetAppVolume.objects.create(
            name='fs-vol-explicit', svm=svm_bare, aggregate=aggregate, tenant=cls.tenant
        )
        cls.vol_unrelated = NetAppVolume.objects.create(
            name='fs-vol-unrelated', svm=svm_bare, aggregate=aggregate
        )

    def _qs(self):
        return NetAppVolume.objects.filter(name__startswith='fs-vol-')

    def test_search_by_name(self):
        fs = VolumeFilterSet({'q': 'fs-vol-explicit'}, queryset=self._qs())
        self.assertEqual(fs.qs.count(), 1)

    def test_filter_by_tenant_includes_direct_and_inherited(self):
        fs = VolumeFilterSet({'tenant_id': [self.tenant.pk]}, queryset=self._qs())
        self.assertEqual(set(fs.qs), {self.vol_inherited, self.vol_explicit})


class QTreeFilterSetTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.create(name='fs-qtree-tenant', slug='fs-qtree-tenant')
        cluster = NetAppCluster.objects.create(name='fs-qtree-cluster')
        node = NetAppNode.objects.create(name='fs-qtree-node', cluster=cluster)
        aggregate = NetAppAggregate.objects.create(name='fs-qtree-aggr', node=node)
        cls.svm = NetAppSVM.objects.create(name='fs-qtree-svm', cluster=cluster, tenant=cls.tenant)
        cls.volume = NetAppVolume.objects.create(name='fs-qtree-vol', svm=cls.svm, aggregate=aggregate)

        NetAppQTree.objects.bulk_create([
            NetAppQTree(name='fs-qtree-1', volume=cls.volume),
            NetAppQTree(name='fs-qtree-2', volume=cls.volume),
        ])

    def _qs(self):
        return NetAppQTree.objects.filter(name__startswith='fs-qtree-')

    def test_search_by_name(self):
        fs = QTreeFilterSet({'q': 'fs-qtree-1'}, queryset=self._qs())
        self.assertEqual(fs.qs.count(), 1)

    def test_filter_by_svm_id(self):
        fs = QTreeFilterSet({'svm_id': [self.svm.pk]}, queryset=self._qs())
        self.assertEqual(fs.qs.count(), 2)

    def test_filter_by_tenant_id_via_svm_inheritance(self):
        fs = QTreeFilterSet({'tenant_id': [self.tenant.pk]}, queryset=self._qs())
        self.assertEqual(fs.qs.count(), 2)


class QuotaFilterSetTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.create(name='fs-quota-tenant', slug='fs-quota-tenant')
        cluster = NetAppCluster.objects.create(name='fs-quota-cluster')
        node = NetAppNode.objects.create(name='fs-quota-node', cluster=cluster)
        aggregate = NetAppAggregate.objects.create(name='fs-quota-aggr', node=node)
        cls.svm = NetAppSVM.objects.create(name='fs-quota-svm', cluster=cluster, tenant=cls.tenant)
        cls.volume = NetAppVolume.objects.create(name='fs-quota-vol', svm=cls.svm, aggregate=aggregate)

        NetAppQuota.objects.create(volume=cls.volume, index='0')
        NetAppQuota.objects.create(volume=cls.volume, index='1')

    def _qs(self):
        return NetAppQuota.objects.filter(volume=self.volume)

    def test_search_by_index(self):
        fs = QuotaFilterSet({'q': '0'}, queryset=self._qs())
        self.assertEqual(fs.qs.count(), 1)

    def test_filter_by_svm_id(self):
        fs = QuotaFilterSet({'svm_id': [self.svm.pk]}, queryset=self._qs())
        self.assertEqual(fs.qs.count(), 2)

    def test_filter_by_tenant_id_via_svm_inheritance(self):
        fs = QuotaFilterSet({'tenant_id': [self.tenant.pk]}, queryset=self._qs())
        self.assertEqual(fs.qs.count(), 2)


class LUNFilterSetTestCase(TestCase):
    """Tenant filtering must resolve through the whole Volume/SVM inheritance chain."""

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.create(name='fs-lun-tenant', slug='fs-lun-tenant')
        cluster = NetAppCluster.objects.create(name='fs-lun-cluster')
        node = NetAppNode.objects.create(name='fs-lun-node', cluster=cluster)
        aggregate = NetAppAggregate.objects.create(name='fs-lun-aggr', node=node)

        svm_tenanted = NetAppSVM.objects.create(name='fs-lun-svm-tenanted', cluster=cluster, tenant=cls.tenant)
        svm_bare = NetAppSVM.objects.create(name='fs-lun-svm-bare', cluster=cluster)

        vol_inherited = NetAppVolume.objects.create(
            name='fs-lun-vol-inherited', svm=svm_tenanted, aggregate=aggregate
        )
        vol_bare = NetAppVolume.objects.create(
            name='fs-lun-vol-bare', svm=svm_bare, aggregate=aggregate
        )

        cls.lun_inherited_via_svm = NetAppLUN.objects.create(
            name='fs-lun-1', volume=vol_inherited, size=1
        )
        cls.lun_explicit = NetAppLUN.objects.create(
            name='fs-lun-2', volume=vol_bare, size=1, tenant=cls.tenant
        )
        cls.lun_unrelated = NetAppLUN.objects.create(name='fs-lun-3', volume=vol_bare, size=1)

    def _qs(self):
        return NetAppLUN.objects.filter(name__startswith='fs-lun-')

    def test_search_by_name(self):
        fs = LUNFilterSet({'q': 'fs-lun-1'}, queryset=self._qs())
        self.assertEqual(fs.qs.count(), 1)

    def test_filter_by_tenant_resolves_through_full_chain(self):
        fs = LUNFilterSet({'tenant_id': [self.tenant.pk]}, queryset=self._qs())
        self.assertEqual(set(fs.qs), {self.lun_inherited_via_svm, self.lun_explicit})
