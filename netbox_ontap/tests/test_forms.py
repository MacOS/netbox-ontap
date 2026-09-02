from django.test import TestCase

from tenancy.models import Tenant

from netbox_ontap.forms import LUNForm, NodeForm, QuotaForm, VolumeForm
from netbox_ontap.models import (
    NetAppAggregate,
    NetAppCluster,
    NetAppHAPair,
    NetAppNode,
    NetAppQTree,
    NetAppSVM,
    NetAppVolume,
)


class VolumeFormTestCase(TestCase):
    """The `tenant` field must be disabled once the parent SVM already has a resolved Tenant,
    since the value would otherwise merely be re-derived from it."""

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.create(name='form-vol-tenant', slug='form-vol-tenant')
        cluster = NetAppCluster.objects.create(name='form-vol-cluster')
        node = NetAppNode.objects.create(name='form-vol-node', cluster=cluster)
        cls.aggregate = NetAppAggregate.objects.create(name='form-vol-aggr', node=node)
        cls.svm_tenanted = NetAppSVM.objects.create(
            name='form-vol-svm-tenanted', cluster=cluster, tenant=cls.tenant
        )
        cls.svm_bare = NetAppSVM.objects.create(name='form-vol-svm-bare', cluster=cluster)

    def test_tenant_field_disabled_when_svm_has_tenant(self):
        volume = NetAppVolume.objects.create(
            name='form-vol-1', svm=self.svm_tenanted, aggregate=self.aggregate
        )
        form = VolumeForm(instance=volume)
        self.assertTrue(form.fields['tenant'].disabled)

    def test_tenant_field_enabled_when_svm_has_no_tenant(self):
        volume = NetAppVolume.objects.create(
            name='form-vol-2', svm=self.svm_bare, aggregate=self.aggregate
        )
        form = VolumeForm(instance=volume)
        self.assertFalse(form.fields['tenant'].disabled)

    def test_tenant_field_enabled_on_add_form(self):
        """No instance yet (add form): the field cannot be disabled before an SVM is chosen."""
        form = VolumeForm()
        self.assertFalse(form.fields['tenant'].disabled)


class LUNFormTestCase(TestCase):
    """Same tenant-field-disabling rule as VolumeForm, but resolved through the parent Volume."""

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.create(name='form-lun-tenant', slug='form-lun-tenant')
        cluster = NetAppCluster.objects.create(name='form-lun-cluster')
        node = NetAppNode.objects.create(name='form-lun-node', cluster=cluster)
        aggregate = NetAppAggregate.objects.create(name='form-lun-aggr', node=node)
        svm = NetAppSVM.objects.create(name='form-lun-svm', cluster=cluster, tenant=cls.tenant)
        cls.volume_inherited = NetAppVolume.objects.create(
            name='form-lun-vol-inherited', svm=svm, aggregate=aggregate
        )

        svm_bare = NetAppSVM.objects.create(name='form-lun-svm-bare', cluster=cluster)
        cls.volume_bare = NetAppVolume.objects.create(
            name='form-lun-vol-bare', svm=svm_bare, aggregate=aggregate
        )

    def test_tenant_field_disabled_when_volume_resolves_tenant_through_svm(self):
        """The Volume itself has no explicit Tenant, but its SVM does - the LUN field must
        still be disabled, proving the check resolves the full chain, not just the raw field."""
        lun = self.volume_inherited.ontap_luns.create(name='form-lun-1', size=1)
        form = LUNForm(instance=lun)
        self.assertTrue(form.fields['tenant'].disabled)

    def test_tenant_field_enabled_when_volume_has_no_tenant(self):
        lun = self.volume_bare.ontap_luns.create(name='form-lun-2', size=1)
        form = LUNForm(instance=lun)
        self.assertFalse(form.fields['tenant'].disabled)


class QuotaFormTestCase(TestCase):
    """Selecting a QTree must realign the Volume field to the QTree's own Volume."""

    @classmethod
    def setUpTestData(cls):
        cluster = NetAppCluster.objects.create(name='form-quota-cluster')
        node = NetAppNode.objects.create(name='form-quota-node', cluster=cluster)
        aggregate = NetAppAggregate.objects.create(name='form-quota-aggr', node=node)
        svm = NetAppSVM.objects.create(name='form-quota-svm', cluster=cluster)
        cls.volume_a = NetAppVolume.objects.create(name='form-quota-vol-a', svm=svm, aggregate=aggregate)
        cls.volume_b = NetAppVolume.objects.create(name='form-quota-vol-b', svm=svm, aggregate=aggregate)
        cls.qtree_a = NetAppQTree.objects.create(name='form-quota-qtree-a', volume=cls.volume_a)

    def test_mismatched_volume_is_realigned_to_qtree_volume(self):
        form = QuotaForm(data={
            'volume': self.volume_b.pk,
            'qtree': self.qtree_a.pk,
            'index': '0',
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['volume'], self.volume_a)

    def test_matching_volume_and_qtree_is_valid(self):
        form = QuotaForm(data={
            'volume': self.volume_a.pk,
            'qtree': self.qtree_a.pk,
            'index': '0',
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_volume_only_without_qtree_is_valid(self):
        form = QuotaForm(data={
            'volume': self.volume_a.pk,
            'index': '0',
        })
        self.assertTrue(form.is_valid(), form.errors)


class NodeFormHAPartnerTestCase(TestCase):
    """NodeForm transparently creates, replaces, and removes an HA Pair via ha_partner."""

    @classmethod
    def setUpTestData(cls):
        cls.cluster = NetAppCluster.objects.create(name='form-ha-cluster')
        cls.node_1 = NetAppNode.objects.create(name='form-ha-node-1', cluster=cls.cluster)
        cls.node_2 = NetAppNode.objects.create(name='form-ha-node-2', cluster=cls.cluster)
        cls.node_3 = NetAppNode.objects.create(name='form-ha-node-3', cluster=cls.cluster)

    def _base_data(self, node):
        return {
            'name': node.name,
            'cluster': node.cluster_id,
        }

    def test_ha_partner_field_initial_is_populated_for_existing_node(self):
        pair = NetAppHAPair.objects.create(node_a=self.node_1, node_b=self.node_2)
        form = NodeForm(instance=self.node_1)
        self.assertEqual(form.fields['ha_partner'].initial, self.node_2.pk)
        pair.delete()

    def test_ha_partner_field_initial_is_none_for_unpaired_node(self):
        form = NodeForm(instance=self.node_1)
        self.assertIsNone(form.fields['ha_partner'].initial)

    def test_save_creates_pair_when_partner_selected(self):
        data = {**self._base_data(self.node_1), 'ha_partner': self.node_2.pk}
        form = NodeForm(data=data, instance=self.node_1)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertEqual(self.node_1.ha_partner, self.node_2)
        NetAppHAPair.objects.filter(node_a=self.node_1).delete()

    def test_save_removes_pair_when_partner_cleared(self):
        pair = NetAppHAPair.objects.create(node_a=self.node_1, node_b=self.node_2)
        data = {**self._base_data(self.node_1), 'ha_partner': ''}
        form = NodeForm(data=data, instance=self.node_1)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        # Check via DB — the Python object's reverse OneToOneField cache is stale after deletion.
        self.assertFalse(NetAppHAPair.objects.filter(node_a=self.node_1).exists())
        self.assertFalse(NetAppHAPair.objects.filter(node_b=self.node_1).exists())

    def test_save_replaces_pair_when_partner_changes(self):
        pair = NetAppHAPair.objects.create(node_a=self.node_1, node_b=self.node_2)
        data = {**self._base_data(self.node_1), 'ha_partner': self.node_3.pk}
        form = NodeForm(data=data, instance=self.node_1)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.node_1.refresh_from_db()
        self.assertEqual(self.node_1.ha_partner, self.node_3)
        self.assertFalse(NetAppHAPair.objects.filter(pk=pair.pk).exists())
        NetAppHAPair.objects.filter(node_a=self.node_1).delete()

    def test_save_is_noop_when_partner_unchanged(self):
        pair = NetAppHAPair.objects.create(node_a=self.node_1, node_b=self.node_2)
        data = {**self._base_data(self.node_1), 'ha_partner': self.node_2.pk}
        form = NodeForm(data=data, instance=self.node_1)
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertTrue(NetAppHAPair.objects.filter(pk=pair.pk).exists())
        pair.delete()
