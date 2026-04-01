from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from netbox.models import NetBoxModel
from tenancy.models import Tenant
from virtualization.models import Cluster

class SVM(NetBoxModel):
    name = models.CharField(
        max_length=100
    )
    description = models.TextField(
        blank=True
    )
    uuid = models.UUIDField(
        verbose_name="ONTAP SVM UUID",
        blank=True,
        null=True,
    )
    
    cluster = models.ForeignKey(
        to=Cluster,
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

    def clean(self):
        super().clean()
        if not self.uuid:
            self.uuid = None

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_ontap:svm', args=[self.pk])
    
class Volume(NetBoxModel):
    prerequisite_models = (
        'netbox_ontap.SVM',
    )

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
    uuid = models.UUIDField(
        blank=True,
        null=True,
        verbose_name="ONTAP Volume UUID"
    )
    svm = models.ForeignKey(
        to=SVM,
        on_delete=models.PROTECT,
        related_name='ontap_volumes'
    )
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

    def clean(self):
        super().clean()
        if not self.uuid:
            self.uuid = None
        if self.tenant and self.svm and self.svm.tenant and self.tenant_id != self.svm.tenant_id:
            raise ValidationError({
                'tenant': 'Tenant of Volume cannot differ from Tenant of SVM.'
            })

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('plugins:netbox_ontap:volume', args=[self.pk])
   
class QTree(NetBoxModel):
    prerequisite_models = (
        'netbox_ontap.Volume',
    )

    name = models.CharField(
        max_length=100
    )
    volume = models.ForeignKey(
        to='Volume',
        on_delete=models.PROTECT,
        related_name='ontap_qtrees'
    )
    description = models.TextField(
        blank=True
    )

    @property
    def svm(self):
        return self.volume.svm

    @property
    def tenant(self):
        if self.volume.tenant_id:
            return self.volume.tenant
        if self.volume.svm and self.volume.svm.tenant_id:
            return self.volume.svm.tenant
        return None

    class Meta:
        verbose_name = 'QTree'
        verbose_name_plural = 'QTrees'
        ordering = ('name', 'volume__name')
        unique_together = ('volume', 'name')

    def __str__(self):
        return f'{self.volume.name}/{self.name}'

    def get_absolute_url(self):
        return reverse('plugins:netbox_ontap:qtree', args=[self.pk])

class Quota(NetBoxModel):
    prerequisite_models = (
        'netbox_ontap.Volume',
    )

    size = models.PositiveBigIntegerField(
        help_text='Size in bytes',
        blank=True,
        null=True
    )
    description = models.TextField(
        blank=True
    )
    volume = models.ForeignKey(
        to=Volume,
        on_delete=models.PROTECT,
        related_name='ontap_quotas',
    )
    qtree = models.ForeignKey(
        to=QTree,
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

    @property
    def tenant(self):
        if self.volume.tenant_id:
            return self.volume.tenant
        if self.volume.svm and self.volume.svm.tenant_id:
            return self.volume.svm.tenant
        return None
    
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
        return reverse('plugins:netbox_ontap:quota', args=[self.pk])
    
    @property
    def display_name(self):
        return str(self)
    
    
class LUN(NetBoxModel):
    name = models.CharField(
        max_length=100
    )
    size = models.PositiveBigIntegerField(
        help_text='Size in bytes'
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
        to=Volume,
        on_delete=models.PROTECT,
        related_name='ontap_luns'
    )
    qtree = models.ForeignKey(
        to=QTree,
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
    uuid = models.UUIDField(
        blank=True,
        null=True,
        verbose_name="ONTAP LUN UUID"
    )

    @property
    def svm(self):
        return self.volume.svm

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

    def _get_effective_tenant_id(self):
        if self.volume.tenant_id:
            return self.volume.tenant_id
        if self.volume.svm and self.volume.svm.tenant_id:
            return self.volume.svm.tenant_id
        return None

    def clean(self):
        super().clean()
        errors = {}

        if not self.uuid:
            self.uuid = None

        effective_tenant_id = self._get_effective_tenant_id()

        if self.tenant_id and effective_tenant_id and self.tenant_id != effective_tenant_id:
            errors['tenant'] = 'Tenant of LUN cannot differ from Tenant of Volume.'

        if self.tenant and self.qtree and self.qtree.volume.tenant and self.tenant_id != self.qtree.volume.tenant_id:
            errors['tenant'] = 'Tenant of LUN cannot differ from Tenant of QTree/Volume.'

        if self.qtree and self.volume and self.qtree.volume_id != self.volume_id:
            errors['qtree'] = 'QTree must belong to the selected Volume.'

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Tenant is derived from the authoritative volume assignment.
        self.tenant_id = self._get_effective_tenant_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} - {self.tenant.name}' if self.tenant else f'{self.name}'

    def get_absolute_url(self):
        return reverse('plugins:netbox_ontap:lun', args=[self.pk])
