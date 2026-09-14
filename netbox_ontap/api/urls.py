# SPDX-FileCopyrightText: 2026 Gabor Somogyvari, Leonhard Kreißig (Deutsche Telekom AG) <leonhard.kreissig@telekom.de>
#
# SPDX-License-Identifier: Apache-2.0

from netbox.api.routers import NetBoxRouter
from . import views


app_name = 'netbox_ontap'

router = NetBoxRouter()
router.register('cluster', views.ClusterViewSet)
router.register('node', views.NodeViewSet)
router.register('aggregate', views.AggregateViewSet)
router.register('svm', views.SVMViewSet)
router.register('volume', views.VolumeViewSet)
router.register('qtree', views.QTreeViewSet)
router.register('quota', views.QuotaViewSet)
router.register('lun', views.LUNViewSet)

urlpatterns = router.urls
