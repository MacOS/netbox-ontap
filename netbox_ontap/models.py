from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from netbox.models import ChangeLoggedModel, NetBoxModel
from tenancy.models import Tenant
from dcim.models import Device
from ipam.models import IPAddress
from utilities.querysets import RestrictedQuerySet


class NullableUUIDMixin(models.Model):
    """Provide an optional UUID field normalized before persistence."""

    uuid = models.UUIDField(
        verbose_name='ONTAP UUID',
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Persist the model with blank UUID values stored as NULL."""
        if not self.uuid:
            self.uuid = None
        super().save(*args, **kwargs)


class NetAppCluster(NullableUUIDMixin, NetBoxModel):
    name = models.CharField(
        max_length=100
    )
    description = models.TextField(
        blank=True
    )
    ontap_version = models.CharField(
        max_length=64,
        blank=True,
        verbose_name="ONTAP Version"
    )
    management_ip = models.ForeignKey(
        to=IPAddress,
        on_delete=models.SET_NULL,
        related_name='ontap_clusters',
        blank=True,
        null=True,
        verbose_name="Management IP"
    )

    class Meta:
        verbose_name = 'Cluster'
        verbose_name_plural = 'Clusters'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=('uuid',),
                condition=models.Q(uuid__isnull=False),
                name='netbox_ontap_cluster_uuid_unique_not_null',
            ),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_ontap:netappcluster', args=[self.pk])


class NetAppNode(NullableUUIDMixin, NetBoxModel):
    prerequisite_models = (
        'netbox_ontap.NetAppCluster',
    )

    name = models.CharField(
        max_length=100
    )
    description = models.TextField(
        blank=True
    )
    cluster = models.ForeignKey(
        to=NetAppCluster,
        on_delete=models.PROTECT,
        related_name='ontap_nodes'
    )
    device = models.OneToOneField(
        to=Device,
        on_delete=models.PROTECT,
        related_name='ontap_node',
        blank=True,
        null=True
    )
    model = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Platform Model"
    )
    serial_number = models.CharField(
        max_length=100,
        blank=True
    )
    management_ip = models.ForeignKey(
        to=IPAddress,
        on_delete=models.SET_NULL,
        related_name='ontap_nodes',
        blank=True,
        null=True,
        verbose_name="Management IP"
    )
    class Meta:
        verbose_name = 'Node'
        verbose_name_plural = 'Nodes'
        ordering = ('cluster__name', 'name')
        unique_together = ('cluster', 'name')
        constraints = [
            models.UniqueConstraint(
                fields=('uuid',),
                condition=models.Q(uuid__isnull=False),
                name='netbox_ontap_node_uuid_unique_not_null',
            ),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_ontap:netappnode', args=[self.pk])

    @property
    def ha_pair(self):
        """Return the HA pair containing this node, if one exists."""
        return getattr(self, 'ha_pair_as_node_a', None) or getattr(self, 'ha_pair_as_node_b', None)

    @property
    def ha_partner(self):
        """Return this node's peer in its HA pair, if one exists."""
        ha_pair = self.ha_pair
        if ha_pair is None:
            return None
        return ha_pair.node_b if ha_pair.node_a_id == self.pk else ha_pair.node_a


class NetAppHAPair(ChangeLoggedModel):
    """Backend-only record linking two HA-partner nodes; not user-facing."""

    _netbox_private = True

    node_a = models.OneToOneField(
        to=NetAppNode,
        on_delete=models.PROTECT,
        related_name='ha_pair_as_node_a',
        verbose_name='Node A'
    )
    node_b = models.OneToOneField(
        to=NetAppNode,
        on_delete=models.PROTECT,
        related_name='ha_pair_as_node_b',
        verbose_name='Node B'
    )

    class Meta:
        verbose_name = 'HA Pair'
        verbose_name_plural = 'HA Pairs'
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(node_a=models.F('node_b')),
                name='netbox_ontap_ha_pair_distinct_nodes',
            ),
        ]

    def clean(self):
        """Ensure the pair has two unique nodes in the same cluster."""
        super().clean()
        if self.node_a_id == self.node_b_id:
            raise ValidationError({'node_b': 'An HA pair must contain two different nodes.'})
        if self.node_a.cluster_id != self.node_b.cluster_id:
            raise ValidationError({'node_b': 'HA pair nodes must belong to the same Cluster.'})

    def __str__(self):
        return f'{self.node_a} / {self.node_b}'


class NetAppAggregate(NullableUUIDMixin, NetBoxModel):
    prerequisite_models = (
        'netbox_ontap.NetAppNode',
    )

    name = models.CharField(
        max_length=100
    )
    description = models.TextField(
        blank=True
    )
    node = models.ForeignKey(
        to=NetAppNode,
        on_delete=models.PROTECT,
        related_name='ontap_aggregates'
    )
    size = models.PositiveBigIntegerField(
        help_text='Size in bytes',
        blank=True,
        null=True
    )

    @property
    def cluster(self):
        return self.node.cluster

    class Meta:
        verbose_name = 'Aggregate'
        verbose_name_plural = 'Aggregates'
        ordering = ('node__name', 'name')
        unique_together = ('node', 'name')
        constraints = [
            models.UniqueConstraint(
                fields=('uuid',),
                condition=models.Q(uuid__isnull=False),
                name='netbox_ontap_aggregate_uuid_unique_not_null',
            ),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_ontap:netappaggregate', args=[self.pk])


class TenantInheritanceMixin:
    """
    Shared behavior for models whose `tenant` may be explicitly assigned on the object
    itself, or left blank (None) to defer to the nearest tenant-bearing ancestor.

    `tenant` is never auto-populated: None always means "deferred", and any other value
    always means "explicitly assigned here". This keeps the two states unambiguous and
    avoids any need to track how a stored value came to be.
    """

    def get_tenant_parent(self):
        """Return the object this model defers to when its own `tenant` is unset, or None."""
        raise NotImplementedError

    def get_tenant_children(self):
        """Return the queryset of direct child objects participating in tenant inheritance."""
        raise NotImplementedError

    def get_tenant(self):
        """Return this object's own Tenant, or the nearest ancestor's, or None."""
        if self.tenant_id:
            return self.tenant
        parent = self.get_tenant_parent()
        return parent.get_tenant() if parent else None

    def get_descendant_tenants(self):
        """Return all Tenants explicitly assigned anywhere within this object's descendants."""
        tenant_ids = set()
        for child in self.get_tenant_children():
            if child.tenant_id:
                tenant_ids.add(child.tenant_id)
            tenant_ids.update(child.get_descendant_tenants().values_list('pk', flat=True))
        return Tenant.objects.filter(pk__in=tenant_ids)

    def clean(self):
        super().clean()

        parent = self.get_tenant_parent()
        parent_tenant = parent.get_tenant() if parent else None

        if self.tenant_id and parent_tenant and self.tenant_id != parent_tenant.id:
            raise ValidationError({
                'tenant': f"Cannot assign Tenant {self.tenant} - "
                          f"parent '{parent}' is assigned to Tenant {parent_tenant}."
            })

        if self.pk is not None:
            resolved_tenant = self.get_tenant()
            conflict = self._find_tenant_conflict(resolved_tenant.id if resolved_tenant else None)
            if conflict:
                raise ValidationError({'tenant': conflict})

    def _find_tenant_conflict(self, tenant_id):
        # Recurses through the whole subtree - a descendant only conflicts if it was
        # explicitly assigned a Tenant (never auto-filled) that differs from mine.
        for child in self.get_tenant_children():
            if child.tenant_id and child.tenant_id != tenant_id:
                return f"'{child}' is explicitly assigned to Tenant {child.tenant}."
            conflict = child._find_tenant_conflict(tenant_id)
            if conflict:
                return conflict
        return None


class NetAppSVM(NullableUUIDMixin, TenantInheritanceMixin, NetBoxModel):
    name = models.CharField(
        max_length=100
    )
    description = models.TextField(
        blank=True
    )
    cluster = models.ForeignKey(
        to=NetAppCluster,
        on_delete=models.PROTECT,
        related_name='ontap_svms',
        blank=True,
        null=True
    )

    tenant = models.ForeignKey(
        to=Tenant,
        on_delete=models.PROTECT,
        related_name='ontap_svms',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'SVM'
        verbose_name_plural = 'SVMs'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=('uuid',),
                condition=models.Q(uuid__isnull=False),
                name='netbox_ontap_svm_uuid_unique_not_null',
            ),
        ]

    def get_tenant_parent(self):
        return None

    def get_tenant_children(self):
        return NetAppVolume.objects.filter(svm_id=self.pk)

    def clean(self):
        super().clean()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_ontap:netappsvm', args=[self.pk])


class NetAppVolumeQuerySet(RestrictedQuerySet):
    def for_tenant(self, tenants):
        """Volumes whose resolved Tenant is in `tenants` (a Tenant or iterable of Tenants),
        whether set directly or inherited from their SVM."""
        tenants = [tenants] if isinstance(tenants, Tenant) else list(tenants)
        return self.filter(
            models.Q(tenant__in=tenants) | models.Q(tenant__isnull=True, svm__tenant__in=tenants)
        )


class NetAppVolume(NullableUUIDMixin, TenantInheritanceMixin, NetBoxModel):
    prerequisite_models = (
        'netbox_ontap.NetAppSVM',
        'netbox_ontap.NetAppAggregate',
    )

    objects = NetAppVolumeQuerySet.as_manager()

    name = models.CharField(
        max_length=100
    )
    description = models.TextField(
        blank=True
    )
    tenant = models.ForeignKey(
        to=Tenant,
        on_delete=models.PROTECT,
        related_name='ontap_volumes',
        blank=True,
        null=True
    )
    svm = models.ForeignKey(
        to=NetAppSVM,
        on_delete=models.PROTECT,
        related_name='ontap_volumes'
    )
    aggregate = models.ForeignKey(
        to=NetAppAggregate,
        on_delete=models.PROTECT,
        related_name='ontap_volumes'
    )
    size = models.PositiveBigIntegerField(
        help_text='Provisioned size in bytes',
        blank=True,
        null=True
    )

    @property
    def node(self):
        return self.aggregate.node

    @property
    def cluster(self):
        return self.aggregate.node.cluster

    class Meta:
        verbose_name = 'Volume'
        verbose_name_plural = 'Volumes'
        ordering = ('name',)
        unique_together = ('svm', 'name')
        constraints = [
            models.UniqueConstraint(
                fields=('uuid',),
                condition=models.Q(uuid__isnull=False),
                name='netbox_ontap_volume_uuid_unique_not_null',
            ),
        ]

    def get_tenant_parent(self):
        return self.svm

    def get_tenant_children(self):
        return NetAppLUN.objects.filter(volume_id=self.pk)

    def clean(self):
        super().clean()

        if self.svm and self.svm.cluster_id and self.aggregate and self.aggregate.node.cluster_id != self.svm.cluster_id:
            raise ValidationError({
                'aggregate': "Aggregate's Node must belong to the same Cluster as the Volume's SVM."
            })

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_ontap:netappvolume', args=[self.pk])
   
class NetAppQTree(NetBoxModel):
    prerequisite_models = (
        'netbox_ontap.NetAppVolume',
    )

    name = models.CharField(
        max_length=100
    )
    volume = models.ForeignKey(
        to=NetAppVolume,
        on_delete=models.PROTECT,
        related_name='ontap_qtrees'
    )
    description = models.TextField(
        blank=True
    )

    @property
    def svm(self):
        return self.volume.svm

    def get_tenant(self):
        return self.volume.get_tenant()

    @property
    def tenant(self):
        return self.get_tenant()

    def get_descendant_tenants(self):
        """Return all Tenants explicitly assigned to this QTree's LUNs."""
        tenant_ids = set(
            NetAppLUN.objects.filter(qtree_id=self.pk)
            .filter(tenant__isnull=False)
            .values_list('tenant_id', flat=True)
        )
        return Tenant.objects.filter(pk__in=tenant_ids)

    class Meta:
        verbose_name = 'QTree'
        verbose_name_plural = 'QTrees'
        ordering = ('name', 'volume__name')
        unique_together = ('volume', 'name')

    def __str__(self):
        return f'{self.volume.name}/{self.name}'

    def get_absolute_url(self):
        return reverse('plugins:netbox_ontap:netappqtree', args=[self.pk])

class NetAppQuota(NetBoxModel):
    prerequisite_models = (
        'netbox_ontap.NetAppVolume',
    )

    space_hard_limit = models.PositiveBigIntegerField(
        help_text='Hard space limit in bytes (blank = metering only, no space limit)',
        blank=True,
        null=True
    )
    space_soft_limit = models.PositiveBigIntegerField(
        help_text='Soft space limit in bytes, triggers a warning before the hard limit is reached',
        blank=True,
        null=True
    )
    files_hard_limit = models.PositiveBigIntegerField(
        help_text='Hard limit on the number of files/inodes',
        blank=True,
        null=True
    )
    files_soft_limit = models.PositiveBigIntegerField(
        help_text='Soft limit on the number of files/inodes, triggers a warning before the hard limit is reached',
        blank=True,
        null=True
    )
    description = models.TextField(
        blank=True
    )
    volume = models.ForeignKey(
        to=NetAppVolume,
        on_delete=models.PROTECT,
        related_name='ontap_quotas',
    )
    qtree = models.ForeignKey(
        to=NetAppQTree,
        on_delete=models.PROTECT,
        related_name='ontap_quotas',
        blank=True,
        null=True,
    )
    index = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Quota Index"
    )

    @property
    def svm(self):
        return self.volume.svm

    def get_tenant(self):
        return self.volume.get_tenant()

    @property
    def tenant(self):
        return self.get_tenant()

    class Meta:
        verbose_name = 'Quota'
        verbose_name_plural = 'Quotas'
        ordering = ('volume__name', 'index')

    def clean(self):
        super().clean()

        if self.qtree and self.volume and self.qtree.volume.id != self.volume.id:
            raise ValidationError({
                'qtree': 'QTree must belong to the selected Volume.'
            })

    def __str__(self):
        if self.qtree:
            return f'{self.volume.name} - {self.qtree.name}'
        return f'{self.volume.name} - Volume level quota'

    def get_absolute_url(self):
        return reverse('plugins:netbox_ontap:netappquota', args=[self.pk])

    @property
    def display_name(self):
        return str(self)


class NetAppLUNQuerySet(RestrictedQuerySet):
    def for_tenant(self, tenants):
        """LUNs whose resolved Tenant is in `tenants` (a Tenant or iterable of Tenants),
        whether set directly or inherited via Volume/SVM."""
        tenants = [tenants] if isinstance(tenants, Tenant) else list(tenants)
        return self.filter(
            models.Q(tenant__in=tenants)
            | models.Q(tenant__isnull=True, volume__tenant__in=tenants)
            | models.Q(tenant__isnull=True, volume__tenant__isnull=True, volume__svm__tenant__in=tenants)
        )


class NetAppLUN(NullableUUIDMixin, TenantInheritanceMixin, NetBoxModel):
    objects = NetAppLUNQuerySet.as_manager()

    OS_TYPE_CHOICES = (
        ('aix', 'AIX'),
        ('hyper_v', 'Hyper-V'),
        ('linux', 'Linux'),
        ('netware', 'NetWare'),
        ('openvms', 'OpenVMS'),
        ('solaris', 'Solaris'),
        ('vmware', 'VMware'),
        ('windows', 'Windows'),
        ('windows_2008', 'Windows 2008'),
        ('windows_gpt', 'Windows GPT'),
        ('xen', 'Xen'),
    )

    name = models.CharField(
        max_length=100
    )
    size = models.PositiveBigIntegerField(
        help_text='Size in bytes'
    )
    os_type = models.CharField(
        max_length=32,
        choices=OS_TYPE_CHOICES,
        blank=True,
        verbose_name="OS Type"
    )
    description = models.TextField(
        blank=True
    )
    wwn = models.CharField(
        max_length=64,
        blank=True,
        verbose_name='WWN'
    )
    volume = models.ForeignKey(
        to=NetAppVolume,
        on_delete=models.PROTECT,
        related_name='ontap_luns'
    )
    qtree = models.ForeignKey(
        to=NetAppQTree,
        on_delete=models.PROTECT,
        related_name='ontap_luns',
        blank=True,
        null=True
    )
    
    tenant = models.ForeignKey(
        to=Tenant,
        on_delete=models.PROTECT,
        related_name='ontap_luns',
        blank=True,
        null=True
    )
    @property
    def svm(self):
        return self.volume.svm

    def get_tenant_parent(self):
        return self.volume

    def get_tenant_children(self):
        return NetAppLUN.objects.none()

    class Meta:
        verbose_name = 'LUN'
        verbose_name_plural = 'LUNs'
        ordering = ('name',)
        unique_together = ('tenant', 'name')
        constraints = [
            models.UniqueConstraint(
                fields=('uuid',),
                condition=models.Q(uuid__isnull=False),
                name='netbox_ontap_lun_uuid_unique_not_null',
            ),
        ]

    def clean(self):
        super().clean()
        errors = {}

        # Validiere QTree gehört zum Volume
        if self.qtree and self.volume and self.qtree.volume_id != self.volume_id:
            errors['qtree'] = 'QTree must belong to the selected Volume.'

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        tenant = self.get_tenant()
        return f'{self.name} - {tenant.name if tenant else "None"}'

    def get_absolute_url(self):
        return reverse('plugins:netbox_ontap:netapplun', args=[self.pk])
