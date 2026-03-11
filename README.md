# Netbox ONTAP

A [Netbox](https://github.com/netbox-community/netbox) plugin for storage related documentation where virtualization is used. 

5 new object types are introduced: 
  - Storage Pools: a pool that is created on a storage. Currently this storage has to be a Netbox Device.
  - LUN: optinally tied to a Storage Pool
  - Quota
  - Datastores: created on LUN(s)
  - Storage Sessions: the "source" of a session is a Netbox Virtualization Cluster, the "destination" is the LUN Group
  - VMDK: can be assigned to a VM and a datastore

# Install

The plugin is not available via pip and must be installed from source.

## Installation Steps

1. Clone the plugin repository:
```bash
cd /opt/netbox
git clone https://gitlab.devops.telekom.de/leonhard.kreissig/netbox-ontap.git
```

2. Install the plugin:
```bash
source /opt/netbox/venv/bin/activate
cd netbox-ontap
pip install -e .
```

3. Add netbox_ontap to PLUGINS in configuration.py:
```python
PLUGINS = ['netbox_ontap']
```

4. Run database migrations:
```bash
cd /opt/netbox/netbox
python3 manage.py migrate
```

5. Collect static files:
```bash
python3 manage.py collectstatic --no-input
```

6. Restart NetBox services:
```bash
sudo systemctl restart netbox netbox-rq
```

**Note:** The paths above assume a standard NetBox installation in `/opt/netbox`. Adjust paths according to your installation.

# Usage

1. Create regular Netbox objects: a storage Device, a virtualization Cluster, and a Virtual Machine
2. Create a Storage Pool that is assigned to the above created Device
3. Create LUN(s), optionally on the Storage Pool
4. Create Datastore(s) on LUNs
5. Create Storage Session between the Cluster and the Datastore
6. Create VMDK on the VM that is on a Cluster that has a Storage Session: this is possible either from the main menu, or on the VM's own page
7. Create Quotas

## Ansible Import Upsert Examples

This repository contains reusable Ansible examples for idempotent imports from external ONTAP automation.

- `examples/ansible/tasks/netbox_plugin_upsert_by_uuid.yml`
  Generic upsert task for plugin objects with a UUID field (`svm`, `volume`, `qtree`, `lun`).
- `examples/ansible/tasks/netbox_plugin_upsert_quota_by_key.yml`
  Quota upsert task using natural key (`qtree_uuid` + `index`) because `Quota` has no dedicated UUID field.
- `examples/ansible/upsert_all_storage_objects.yml`
  End-to-end example playbook using both task files.
