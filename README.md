# NetBox ONTAP

A [NetBox](https://github.com/netbox-community/netbox) plugin for documenting NetApp ONTAP storage infrastructure alongside existing virtualization resources.

**Minimum NetBox version: 4.3.0**

## Data Model

The plugin introduces 5 new object types that map directly to ONTAP concepts:

| Object     | ONTAP Equivalent        | Key Relations                                                            |
|------------|-------------------------|--------------------------------------------------------------------------|
| **SVM**    | Storage Virtual Machine | linked to a NetBox Virtualization Cluster and optionally a Tenant        |
| **Volume** | ONTAP Volume            | belongs to an SVM; inherits Tenant from SVM                              |
| **QTree**  | Qtree                   | belongs to a Volume; unique per Volume                                   |
| **Quota**  | Quota rule              | belongs to a QTree; identified by QTree + Index                          |
| **LUN**    | LUN                     | belongs to a Volume and optionally a QTree; carries size (bytes) and WWN |

SVMs and Volumes support a UUID field for correlation with live ONTAP data. QTrees have no UUID in ONTAP and are identified by their natural key (Volume + Name), Quotas are identified by the combination of Volume and Index.

### Tenant propagation

Tenant is authoritative at the SVM level and propagates downward:

```
SVM (tenant) → Volume (inherits) → LUN (inherits)
```

A `ValidationError` is raised if a manually set Tenant contradicts the inherited one.

### UI extensions

The plugin adds a **Storage** card on the detail pages of:

- **Virtualization Cluster** – shows the SVMs, Volumes, and LUNs associated with the cluster.
- **Tenant** – shows all SVMs, Volumes, LUNs, and Quotas for the tenant, including a total quota size.

---

## Installation

The plugin is not available on PyPI and must be installed from source.

### Steps

1. Clone the repository into your NetBox server:

```bash
cd /opt/netbox
git clone https://gitlab.devops.telekom.de/leonhard.kreissig/netbox-ontap.git
```

2. Install the package into the NetBox virtual environment:

```bash
source /opt/netbox/venv/bin/activate
cd netbox-ontap
pip install -e .
```

3. Register the plugin in `configuration.py`:

```python
PLUGINS = ['netbox_ontap']
```

4. Apply database migrations:

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

> Paths above assume a standard installation under `/opt/netbox`. Adjust as needed.

---

## Usage

### Manual workflow

1. Ensure a NetBox **Virtualization Cluster** and a **Tenant** already exist.
2. Create an **SVM**, assign it to the Cluster and optionally a Tenant.
3. Create **Volume(s)** under the SVM.
4. Create **QTree(s)** under a Volume.
5. Create **Quota(s)** for a QTree (specify size in bytes and an index).
6. Create **LUN(s)** under a Volume, optionally scoped to a QTree.

All five object types are accessible from the **Storage** navigation menu (NAS icon).

### REST API

The plugin exposes a full CRUD API under:

```
/api/plugins/ontap/<endpoint>/
```

Supported endpoints: `svm`, `volume`, `qtree`, `quota`, `lun`.
