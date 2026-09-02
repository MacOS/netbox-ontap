import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models

PLACEHOLDER_NOTE = (
    'Auto-created during migration for pre-existing data that predates this relation. '
    'Reassign to the real object once known, then this placeholder can be deleted. '
    'If this placeholder has no relations, you can safely delete it without affecting any other objects.'
)


def noop(apps, schema_editor):
    pass


def transform_svm_clusters(apps, schema_editor):
    # SVM.cluster is being repointed from virtualization.Cluster to NetAppCluster. Create a
    # matching NetAppCluster (reusing the same primary key) for every previously-linked
    # virtualization Cluster, so existing SVM->Cluster relations survive the FK retarget
    # without ever needing to rewrite the SVM rows themselves.
    NetAppSVM = apps.get_model('netbox_ontap', 'NetAppSVM')
    NetAppCluster = apps.get_model('netbox_ontap', 'NetAppCluster')
    VirtualizationCluster = apps.get_model('virtualization', 'Cluster')

    old_cluster_ids = NetAppSVM.objects.exclude(cluster_id=None).values_list('cluster_id', flat=True).distinct()
    for old_id in old_cluster_ids:
        try:
            name = VirtualizationCluster.objects.get(pk=old_id).name
        except VirtualizationCluster.DoesNotExist:
            name = f'Unknown Cluster {old_id}'
        NetAppCluster.objects.create(
            pk=old_id,
            name=name,
            description='Auto-created during migration from the previously linked Virtualization Cluster.',
        )


def backfill_volume_aggregate(apps, schema_editor):
    # Volumes predating the Aggregate relation have no real Aggregate to point to; give each
    # affected Cluster exactly one placeholder Node + Aggregate and assign it. Volumes whose
    # SVM has no Cluster at all fall back to one shared placeholder Cluster.
    NetAppVolume = apps.get_model('netbox_ontap', 'NetAppVolume')
    unassigned = NetAppVolume.objects.filter(aggregate_id=None)
    if not unassigned.exists():
        return

    NetAppCluster = apps.get_model('netbox_ontap', 'NetAppCluster')
    NetAppNode = apps.get_model('netbox_ontap', 'NetAppNode')
    NetAppAggregate = apps.get_model('netbox_ontap', 'NetAppAggregate')

    aggregate_by_cluster_id = {}
    fallback_cluster = {}

    def get_placeholder_aggregate(cluster):
        if cluster.id not in aggregate_by_cluster_id:
            node, _ = NetAppNode.objects.get_or_create(
                cluster=cluster,
                name='legacy-unassigned',
                defaults={'description': PLACEHOLDER_NOTE},
            )
            aggregate, _ = NetAppAggregate.objects.get_or_create(
                node=node,
                name='legacy_unassigned',
                defaults={'description': PLACEHOLDER_NOTE},
            )
            aggregate_by_cluster_id[cluster.id] = aggregate
        return aggregate_by_cluster_id[cluster.id]

    def get_fallback_cluster():
        if 'cluster' not in fallback_cluster:
            fallback_cluster['cluster'], _ = NetAppCluster.objects.get_or_create(
                name='Legacy (unassigned)',
                defaults={'description': PLACEHOLDER_NOTE},
            )
        return fallback_cluster['cluster']

    for volume in unassigned:
        cluster = volume.svm.cluster if volume.svm.cluster_id else get_fallback_cluster()
        volume.aggregate = get_placeholder_aggregate(cluster)
        volume.save(update_fields=['aggregate'])


class Migration(migrations.Migration):

    dependencies = [
        ('dcim', '0207_remove_redundant_indexes'),
        ('extras', '0128_tableconfig'),
        ('ipam', '0081_remove_service_device_virtual_machine_add_parent_gfk_index'),
        ('netbox_ontap', '0002_alter_volume_unique_together'),
        ('tenancy', '0020_remove_contactgroupmembership'),
        ('virtualization', '0048_populate_mac_addresses'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='LUN',
            new_name='NetAppLUN',
        ),
        migrations.RenameModel(
            old_name='QTree',
            new_name='NetAppQTree',
        ),
        migrations.RenameModel(
            old_name='Quota',
            new_name='NetAppQuota',
        ),
        migrations.RenameModel(
            old_name='SVM',
            new_name='NetAppSVM',
        ),
        migrations.RenameModel(
            old_name='Volume',
            new_name='NetAppVolume',
        ),
        migrations.RenameField(
            model_name='netappquota',
            old_name='size',
            new_name='space_hard_limit',
        ),
        migrations.AlterField(
            model_name='netappquota',
            name='space_hard_limit',
            field=models.PositiveBigIntegerField(blank=True, help_text='Hard space limit in bytes (blank = metering only, no space limit)', null=True),
        ),
        migrations.AddField(
            model_name='netappquota',
            name='space_soft_limit',
            field=models.PositiveBigIntegerField(blank=True, help_text='Soft space limit in bytes, triggers a warning before the hard limit is reached', null=True),
        ),
        migrations.AddField(
            model_name='netappquota',
            name='files_hard_limit',
            field=models.PositiveBigIntegerField(blank=True, help_text='Hard limit on the number of files/inodes', null=True),
        ),
        migrations.AddField(
            model_name='netappquota',
            name='files_soft_limit',
            field=models.PositiveBigIntegerField(blank=True, help_text='Soft limit on the number of files/inodes, triggers a warning before the hard limit is reached', null=True),
        ),
        migrations.AddField(
            model_name='netapplun',
            name='os_type',
            field=models.CharField(
                blank=True,
                choices=[
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
                ],
                max_length=32,
                verbose_name='OS Type',
            ),
        ),
        migrations.AddField(
            model_name='netappvolume',
            name='size',
            field=models.PositiveBigIntegerField(blank=True, help_text='Provisioned size in bytes', null=True),
        ),
        migrations.AlterField(
            model_name='netapplun',
            name='uuid',
            field=models.UUIDField(blank=True, null=True, verbose_name='ONTAP UUID'),
        ),
        migrations.AlterField(
            model_name='netappsvm',
            name='uuid',
            field=models.UUIDField(blank=True, null=True, verbose_name='ONTAP UUID'),
        ),
        migrations.AlterField(
            model_name='netappvolume',
            name='uuid',
            field=models.UUIDField(blank=True, null=True, verbose_name='ONTAP UUID'),
        ),
        migrations.CreateModel(
            name='NetAppCluster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('uuid', models.UUIDField(blank=True, null=True, verbose_name='ONTAP UUID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('ontap_version', models.CharField(blank=True, max_length=64, verbose_name='ONTAP Version')),
                ('management_ip', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ontap_clusters', to='ipam.ipaddress', verbose_name='Management IP')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Cluster',
                'verbose_name_plural': 'Clusters',
                'ordering': ('name',),
            },
        ),
        migrations.RunPython(transform_svm_clusters, noop),
        migrations.AlterField(
            model_name='netappsvm',
            name='cluster',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ontap_svms', to='netbox_ontap.netappcluster'),
        ),
        migrations.AddConstraint(
            model_name='netappcluster',
            constraint=models.UniqueConstraint(condition=models.Q(('uuid__isnull', False)), fields=('uuid',), name='netbox_ontap_cluster_uuid_unique_not_null'),
        ),
        migrations.CreateModel(
            name='NetAppNode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('uuid', models.UUIDField(blank=True, null=True, verbose_name='ONTAP UUID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('model', models.CharField(blank=True, max_length=100, verbose_name='Platform Model')),
                ('serial_number', models.CharField(blank=True, max_length=100)),
                ('cluster', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ontap_nodes', to='netbox_ontap.netappcluster')),
                ('device', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ontap_node', to='dcim.device')),
                ('management_ip', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ontap_nodes', to='ipam.ipaddress', verbose_name='Management IP')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Node',
                'verbose_name_plural': 'Nodes',
                'ordering': ('cluster__name', 'name'),
            },
        ),
        migrations.AddConstraint(
            model_name='netappnode',
            constraint=models.UniqueConstraint(condition=models.Q(('uuid__isnull', False)), fields=('uuid',), name='netbox_ontap_node_uuid_unique_not_null'),
        ),
        migrations.AlterUniqueTogether(
            name='netappnode',
            unique_together={('cluster', 'name')},
        ),
        migrations.CreateModel(
            name='NetAppAggregate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('custom_field_data', models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
                ('uuid', models.UUIDField(blank=True, null=True, verbose_name='ONTAP UUID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('size', models.PositiveBigIntegerField(blank=True, help_text='Size in bytes', null=True)),
                ('node', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ontap_aggregates', to='netbox_ontap.netappnode')),
                ('tags', taggit.managers.TaggableManager(through='extras.TaggedItem', to='extras.Tag')),
            ],
            options={
                'verbose_name': 'Aggregate',
                'verbose_name_plural': 'Aggregates',
                'ordering': ('node__name', 'name'),
            },
        ),
        migrations.AddConstraint(
            model_name='netappaggregate',
            constraint=models.UniqueConstraint(condition=models.Q(('uuid__isnull', False)), fields=('uuid',), name='netbox_ontap_aggregate_uuid_unique_not_null'),
        ),
        migrations.AlterUniqueTogether(
            name='netappaggregate',
            unique_together={('node', 'name')},
        ),
        migrations.AddField(
            model_name='netappvolume',
            name='aggregate',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='ontap_volumes', to='netbox_ontap.netappaggregate'),
        ),
        migrations.RunPython(backfill_volume_aggregate, noop),
        migrations.AlterField(
            model_name='netappvolume',
            name='aggregate',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='ontap_volumes', to='netbox_ontap.netappaggregate'),
        ),
        migrations.CreateModel(
            name='NetAppHAPair',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('node_a', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='ha_pair_as_node_a', to='netbox_ontap.netappnode', verbose_name='Node A')),
                ('node_b', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='ha_pair_as_node_b', to='netbox_ontap.netappnode', verbose_name='Node B')),
            ],
            options={
                'verbose_name': 'HA Pair',
                'verbose_name_plural': 'HA Pairs',
                'constraints': [models.CheckConstraint(condition=models.Q(('node_a', models.F('node_b')), _negated=True), name='netbox_ontap_ha_pair_distinct_nodes')],
            },
        ),
    ]
