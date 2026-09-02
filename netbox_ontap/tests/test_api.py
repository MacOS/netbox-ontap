from django.urls import reverse

from tenancy.models import Tenant
from utilities.testing import APITestCase, APIViewTestCases

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


class AppTest(APITestCase):

    def test_root(self):
        url = reverse('plugins-api:netbox_ontap-api:api-root')
        response = self.client.get(f'{url}?format=api', **self.header)
        self.assertEqual(response.status_code, 200)


class OntapAPITestCase:
    """Shared plugin API namespace for all netbox_ontap model tests."""
    view_namespace = 'plugins-api:netbox_ontap'


class ClusterTest(
    OntapAPITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = NetAppCluster
    brief_fields = ['display', 'id', 'name', 'url', 'uuid']

    @classmethod
    def setUpTestData(cls):
        NetAppCluster.objects.create(name='Cluster 1')
        NetAppCluster.objects.create(name='Cluster 2')
        NetAppCluster.objects.create(name='Cluster 3')

        cls.create_data = [
            {'name': 'Cluster 4'},
            {'name': 'Cluster 5'},
            {'name': 'Cluster 6'},
        ]
        cls.update_data = {'name': 'Cluster 1 (Updated)'}


class NodeTest(
    OntapAPITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = NetAppNode
    brief_fields = ['cluster', 'display', 'id', 'name', 'url', 'uuid']

    @classmethod
    def setUpTestData(cls):
        cluster = NetAppCluster.objects.create(name='Cluster 1')

        NetAppNode.objects.create(name='Node 1', cluster=cluster)
        NetAppNode.objects.create(name='Node 2', cluster=cluster)
        NetAppNode.objects.create(name='Node 3', cluster=cluster)

        cls.create_data = [
            {'name': 'Node 4', 'cluster': cluster.pk},
            {'name': 'Node 5', 'cluster': cluster.pk},
            {'name': 'Node 6', 'cluster': cluster.pk},
        ]
        cls.update_data = {'name': 'Node 1 (Updated)', 'cluster': cluster.pk}


class NodeHAPartnerAPITestCase(OntapAPITestCase, APITestCase):
    """Node API must expose ha_partner inline and return null when unpaired."""

    user_permissions = ('netbox_ontap.view_netappnode',)

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cluster = NetAppCluster.objects.create(name='api-ha-cluster')
        cls.node_a = NetAppNode.objects.create(name='api-ha-node-a', cluster=cluster)
        cls.node_b = NetAppNode.objects.create(name='api-ha-node-b', cluster=cluster)
        cls.node_solo = NetAppNode.objects.create(name='api-ha-node-solo', cluster=cluster)
        cls.pair = NetAppHAPair.objects.create(node_a=cls.node_a, node_b=cls.node_b)

    def _get_node(self, node):
        url = reverse('plugins-api:netbox_ontap-api:netappnode-detail', kwargs={'pk': node.pk})
        return self.client.get(url, **self.header)

    def test_paired_node_exposes_ha_partner(self):
        response = self._get_node(self.node_a)
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.data['ha_partner'])
        self.assertEqual(response.data['ha_partner']['name'], self.node_b.name)

    def test_ha_partner_is_symmetric(self):
        response = self._get_node(self.node_b)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['ha_partner']['name'], self.node_a.name)

    def test_unpaired_node_returns_null_ha_partner(self):
        response = self._get_node(self.node_solo)
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data['ha_partner'])

    def test_ha_pair_has_no_direct_api_endpoint(self):
        url = reverse('plugins-api:netbox_ontap-api:api-root')
        response = self.client.get(f'{url}?format=json', **self.header)
        self.assertNotIn('ha-pair', response.data)


class AggregateTest(
    OntapAPITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = NetAppAggregate
    brief_fields = ['display', 'id', 'name', 'node', 'size', 'url']

    @classmethod
    def setUpTestData(cls):
        cluster = NetAppCluster.objects.create(name='Cluster 1')
        node = NetAppNode.objects.create(name='Node 1', cluster=cluster)

        NetAppAggregate.objects.create(name='Aggr 1', node=node)
        NetAppAggregate.objects.create(name='Aggr 2', node=node)
        NetAppAggregate.objects.create(name='Aggr 3', node=node)

        cls.create_data = [
            {'name': 'Aggr 4', 'node': node.pk},
            {'name': 'Aggr 5', 'node': node.pk},
            {'name': 'Aggr 6', 'node': node.pk},
        ]
        cls.update_data = {'name': 'Aggr 1 (Updated)', 'node': node.pk}


class SVMTest(
    OntapAPITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = NetAppSVM
    brief_fields = ['cluster', 'display', 'id', 'name', 'tenant', 'url', 'uuid']

    @classmethod
    def setUpTestData(cls):
        cluster = NetAppCluster.objects.create(name='Cluster 1')
        tenant = Tenant.objects.create(name='Tenant 1', slug='tenant-1')

        NetAppSVM.objects.create(name='SVM 1', cluster=cluster)
        NetAppSVM.objects.create(name='SVM 2', cluster=cluster)
        NetAppSVM.objects.create(name='SVM 3', cluster=cluster)

        cls.create_data = [
            {'name': 'SVM 4', 'cluster': cluster.pk, 'tenant': tenant.pk},
            {'name': 'SVM 5', 'cluster': cluster.pk},
            {'name': 'SVM 6', 'cluster': cluster.pk},
        ]
        cls.update_data = {'name': 'SVM 1 (Updated)', 'cluster': cluster.pk}


class VolumeTest(
    OntapAPITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = NetAppVolume
    brief_fields = ['aggregate', 'display', 'id', 'name', 'svm', 'tenant', 'url', 'uuid']
    validation_excluded_fields = ['tenant']  # `tenant` always reads as the resolved value, never the raw input

    @classmethod
    def setUpTestData(cls):
        cluster = NetAppCluster.objects.create(name='Cluster 1')
        node = NetAppNode.objects.create(name='Node 1', cluster=cluster)
        aggregate = NetAppAggregate.objects.create(name='Aggr 1', node=node)
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=cluster)

        NetAppVolume.objects.create(name='Vol 1', svm=svm, aggregate=aggregate)
        NetAppVolume.objects.create(name='Vol 2', svm=svm, aggregate=aggregate)
        NetAppVolume.objects.create(name='Vol 3', svm=svm, aggregate=aggregate)

        cls.create_data = [
            {'name': 'Vol 4', 'svm': svm.pk, 'aggregate': aggregate.pk},
            {'name': 'Vol 5', 'svm': svm.pk, 'aggregate': aggregate.pk},
            {'name': 'Vol 6', 'svm': svm.pk, 'aggregate': aggregate.pk},
        ]
        cls.update_data = {'name': 'Vol 1 (Updated)', 'svm': svm.pk, 'aggregate': aggregate.pk}


class QTreeTest(
    OntapAPITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = NetAppQTree
    brief_fields = ['display', 'id', 'name', 'url', 'volume']

    @classmethod
    def setUpTestData(cls):
        cluster = NetAppCluster.objects.create(name='Cluster 1')
        node = NetAppNode.objects.create(name='Node 1', cluster=cluster)
        aggregate = NetAppAggregate.objects.create(name='Aggr 1', node=node)
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=cluster)
        volume = NetAppVolume.objects.create(name='Vol 1', svm=svm, aggregate=aggregate)

        NetAppQTree.objects.create(name='QTree 1', volume=volume)
        NetAppQTree.objects.create(name='QTree 2', volume=volume)
        NetAppQTree.objects.create(name='QTree 3', volume=volume)

        cls.create_data = [
            {'name': 'QTree 4', 'volume': volume.pk},
            {'name': 'QTree 5', 'volume': volume.pk},
            {'name': 'QTree 6', 'volume': volume.pk},
        ]
        cls.update_data = {'name': 'QTree 1 (Updated)', 'volume': volume.pk}


class QuotaTest(
    OntapAPITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = NetAppQuota
    brief_fields = ['display', 'id', 'index', 'qtree', 'space_hard_limit', 'url', 'volume']

    @classmethod
    def setUpTestData(cls):
        cluster = NetAppCluster.objects.create(name='Cluster 1')
        node = NetAppNode.objects.create(name='Node 1', cluster=cluster)
        aggregate = NetAppAggregate.objects.create(name='Aggr 1', node=node)
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=cluster)
        volume = NetAppVolume.objects.create(name='Vol 1', svm=svm, aggregate=aggregate)

        NetAppQuota.objects.create(volume=volume, index='0')
        NetAppQuota.objects.create(volume=volume, index='1')
        NetAppQuota.objects.create(volume=volume, index='2')

        cls.create_data = [
            {'volume': volume.pk, 'index': '3'},
            {'volume': volume.pk, 'index': '4'},
            {'volume': volume.pk, 'index': '5'},
        ]
        cls.update_data = {'volume': volume.pk, 'index': '0', 'space_hard_limit': 1000}


class LUNTest(
    OntapAPITestCase,
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    model = NetAppLUN
    brief_fields = ['display', 'id', 'name', 'qtree', 'size', 'tenant', 'url', 'uuid', 'volume']
    validation_excluded_fields = ['tenant']  # `tenant` always reads as the resolved value, never the raw input

    @classmethod
    def setUpTestData(cls):
        cluster = NetAppCluster.objects.create(name='Cluster 1')
        node = NetAppNode.objects.create(name='Node 1', cluster=cluster)
        aggregate = NetAppAggregate.objects.create(name='Aggr 1', node=node)
        svm = NetAppSVM.objects.create(name='SVM 1', cluster=cluster)
        volume = NetAppVolume.objects.create(name='Vol 1', svm=svm, aggregate=aggregate)

        NetAppLUN.objects.create(name='LUN 1', volume=volume, size=100)
        NetAppLUN.objects.create(name='LUN 2', volume=volume, size=100)
        NetAppLUN.objects.create(name='LUN 3', volume=volume, size=100)

        cls.create_data = [
            {'name': 'LUN 4', 'volume': volume.pk, 'size': 100},
            {'name': 'LUN 5', 'volume': volume.pk, 'size': 100},
            {'name': 'LUN 6', 'volume': volume.pk, 'size': 100},
        ]
        cls.update_data = {'name': 'LUN 1 (Updated)', 'volume': volume.pk, 'size': 200}
