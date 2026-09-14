<!--
SPDX-FileCopyrightText: 2026 Gabor Somogyvari, Leonhard Kreißig (Deutsche Telekom AG) <leonhard.kreissig@telekom.de>

SPDX-License-Identifier: Apache-2.0
-->

# NetBox ONTAP

A [NetBox](https://github.com/netbox-community/netbox) plugin for documenting NetApp ONTAP storage infrastructure alongside existing virtualization resources. This plugin is a Fork of Gabor Somogyvari's general [netbox-storage](https://github.com/viroge/netbox-storage) plugin.  

[![REUSE Compliance Check](../../actions/workflows/reuse-compliance.yml/badge.svg)](../../actions/workflows/reuse-compliance.yml)
[![OpenSSF Scorecard Score](https://api.scorecard.dev/projects/github.com/telekom/netbox-ontap/badge)](https://scorecard.dev/viewer/?uri=github.com/telekom/netbox-ontap/badge)

**Minimum NetBox version: 4.3.0**

## Data Model

The plugin introduces 9 object types that map to ONTAP concepts:

| Object        | ONTAP Equivalent        | Key Relations                                                            |
|---------------|-------------------------|--------------------------------------------------------------------------|
| **Cluster**   | ONTAP Cluster           | optional Management IP (`ipam.IPAddress`); supports NetBox Contacts     |
| **Node**      | Cluster Node            | belongs to a Cluster; optional 1:1 link to a DCIM Device                |
| **HA Pair**   | ONTAP HA pair           | two distinct Nodes from the same Cluster; each Node can join one pair   |
| **Aggregate** | Storage Aggregate       | belongs to a Node                                                        |
| **SVM**       | Storage Virtual Machine | belongs to a Cluster and optionally a Tenant                             |
| **Volume**    | ONTAP Volume            | belongs to an SVM and an Aggregate; inherits Tenant from SVM; optional provisioned size (bytes) |
| **QTree**     | Qtree                   | belongs to a Volume; unique per Volume                                   |
| **Quota**     | Quota rule              | belongs to a Volume and optionally a QTree; carries optional space and file hard/soft limits |
| **LUN**       | LUN                     | belongs to a Volume and optionally a QTree; carries size (bytes), WWN, and OS type |

Cluster, Node, Aggregate, SVM and Volume support a UUID field for correlation with live ONTAP data. QTrees have no UUID in ONTAP and are identified by their natural key (Volume + Name), Quotas are identified by the combination of Volume and Index.

A Volume's Aggregate must belong to the same Cluster as the Volume's SVM; a `ValidationError` is raised otherwise. An HA Pair's Nodes must belong to the same Cluster and may not be identical.

### Physical location

A Cluster's physical location is derived through its Nodes (`Node.device.site`), not stored redundantly on the Cluster itself.

### Tenant propagation

Tenant is authoritative at the SVM level and propagates downward:

```
SVM (tenant) → Volume (inherits) → LUN (inherits)
```

A `ValidationError` is raised if a manually set Tenant contradicts the inherited one.

### UI extensions

The plugin adds a **Storage** card on the detail page of:

- **Tenant** – shows all SVMs, Volumes, LUNs, and Quotas for the tenant, including a total quota size.

---

## Installation

The plugin is not yet available on PyPI and must be installed from source.

### Steps

1. Clone the repository into your NetBox server:

```bash
cd /opt/netbox
git clone https://github.com/telekom/netbox-ontap.git
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

> Paths above assume a standard installation under `/opt/netbox`. Adjust as needed. You don't neccessarily need to have the plugin within your netbox directory and can place it anywhere on your machine, but keeping it nearby to NetBox might be smart.

---

## Usage

### Manual workflow

1. Create a **Cluster** (optionally set a Management IP and assign Contacts).
2. Create **Node(s)** under the Cluster, optionally linking each to a DCIM Device.
3. Create **Aggregate(s)** under a Node.
4. Create an **SVM**, assign it to the Cluster and optionally a Tenant.
5. Create **Volume(s)** under the SVM and an Aggregate belonging to the same Cluster.
6. Create **QTree(s)** under a Volume.
7. Create **Quota(s)** for a Volume, optionally scoped to a QTree (specify optional space/file hard and soft limits and an index).
8. Create **LUN(s)** under a Volume, optionally scoped to a QTree.

All nine object types are accessible from the **Cluster** and **Storage** navigation menu groups (NAS icon).

### REST API

The plugin exposes a full CRUD API under:

```
/api/plugins/ontap/<endpoint>/
```

Supported endpoints: `cluster`, `node`, `ha-pair`, `aggregate`, `svm`, `volume`, `qtree`, `quota`, `lun`.


## Code of Conduct

This project has adopted the [Contributor Covenant](https://www.contributor-covenant.org/) in version 2.1 as our code of conduct. Please see the details in our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). All contributors must abide by the code of conduct.

By participating in this project, you agree to abide by its [Code of Conduct](./CODE_OF_CONDUCT.md) at all times.

## Licensing
Copyright (c) 2026 Gabor Somogyvari, Deutsche Telekom AG

All content in this repository is licensed under at least one of the licenses found in [./LICENSES](./LICENSES); you may not use this file, or any other file in this repository, except in compliance with the Licenses. 
You may obtain a copy of the Licenses by reviewing the files found in the [./LICENSES](./LICENSES) folder.

Unless required by applicable law or agreed to in writing, software distributed under the Licenses is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See in the [./LICENSES](./LICENSES) folder for the specific language governing permissions and limitations under the Licenses.

This project follows the [REUSE standard for software licensing](https://reuse.software/). 
Each file contains copyright and license information, and license texts can be found in the [./LICENSES](./LICENSES) folder. For more information visit https://reuse.software/.
You can find a guide for developers at https://telekom.github.io/reuse-template/.
