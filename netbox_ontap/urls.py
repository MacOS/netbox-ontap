from django.urls import path

from netbox.views.generic import ObjectChangeLogView

from . import models, views


urlpatterns = (
    path("cluster/", views.ClusterListView.as_view(), name="netappcluster_list"),
    path("cluster/add/", views.ClusterEditView.as_view(), name="netappcluster_add"),
    path("cluster/import/", views.ClusterImportView.as_view(), name="netappcluster_import"),
    path("cluster/<int:pk>/", views.ClusterView.as_view(), name="netappcluster"),
    path("cluster/<int:pk>/edit/", views.ClusterEditView.as_view(), name="netappcluster_edit"),
    path("cluster/<int:pk>/delete/", views.ClusterDeleteView.as_view(), name="netappcluster_delete"),
    path("cluster/delete/", views.ClusterBulkDeleteView.as_view(), name="netappcluster_bulk_delete"),
    path(
        "cluster/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="netappcluster_changelog",
        kwargs={"model": models.NetAppCluster},
    ),

    path("node/", views.NodeListView.as_view(), name="netappnode_list"),
    path("node/add/", views.NodeEditView.as_view(), name="netappnode_add"),
    path("node/import/", views.NodeImportView.as_view(), name="netappnode_import"),
    path("node/<int:pk>/", views.NodeView.as_view(), name="netappnode"),
    path("node/<int:pk>/edit/", views.NodeEditView.as_view(), name="netappnode_edit"),
    path("node/<int:pk>/delete/", views.NodeDeleteView.as_view(), name="netappnode_delete"),
    path("node/delete/", views.NodeBulkDeleteView.as_view(), name="netappnode_bulk_delete"),
    path(
        "node/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="netappnode_changelog",
        kwargs={"model": models.NetAppNode},
    ),

    path("aggregate/", views.AggregateListView.as_view(), name="netappaggregate_list"),
    path("aggregate/add/", views.AggregateEditView.as_view(), name="netappaggregate_add"),
    path("aggregate/import/", views.AggregateImportView.as_view(), name="netappaggregate_import"),
    path("aggregate/<int:pk>/", views.AggregateView.as_view(), name="netappaggregate"),
    path("aggregate/<int:pk>/edit/", views.AggregateEditView.as_view(), name="netappaggregate_edit"),
    path("aggregate/<int:pk>/delete/", views.AggregateDeleteView.as_view(), name="netappaggregate_delete"),
    path("aggregate/delete/", views.AggregateBulkDeleteView.as_view(), name="netappaggregate_bulk_delete"),
    path(
        "aggregate/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="netappaggregate_changelog",
        kwargs={"model": models.NetAppAggregate},
    ),

    path("svm/", views.SVMListView.as_view(), name="netappsvm_list"),
    path("svm/add/", views.SVMEditView.as_view(), name="netappsvm_add"),
    path("svm/import/", views.SVMImportView.as_view(), name="netappsvm_import"),
    path("svm/<int:pk>/", views.SVMView.as_view(), name="netappsvm"),
    path("svm/<int:pk>/edit/", views.SVMEditView.as_view(), name="netappsvm_edit"),
    path("svm/<int:pk>/delete/", views.SVMDeleteView.as_view(), name="netappsvm_delete"),
    path("svm/delete/", views.SVMBulkDeleteView.as_view(), name="netappsvm_bulk_delete"),
    path(
        "svm/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="netappsvm_changelog",
        kwargs={"model": models.NetAppSVM},
    ),

    path("volume/", views.VolumeListView.as_view(), name="netappvolume_list"),
    path("volume/add/", views.VolumeEditView.as_view(), name="netappvolume_add"),
    path("volume/import/", views.VolumeImportView.as_view(), name="netappvolume_import"),
    path("volume/<int:pk>/", views.VolumeView.as_view(), name="netappvolume"),
    path("volume/<int:pk>/edit/", views.VolumeEditView.as_view(), name="netappvolume_edit"),
    path("volume/<int:pk>/delete/", views.VolumeDeleteView.as_view(), name="netappvolume_delete"),
    path("volume/delete/", views.VolumeBulkDeleteView.as_view(), name="netappvolume_bulk_delete"),
    path(
        "volume/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="netappvolume_changelog",
        kwargs={"model": models.NetAppVolume},
    ),

    path("qtree/", views.QTreeListView.as_view(), name="netappqtree_list"),
    path("qtree/add/", views.QTreeEditView.as_view(), name="netappqtree_add"),
    path("qtree/import/", views.QTreeImportView.as_view(), name="netappqtree_import"),
    path("qtree/<int:pk>/", views.QTreeView.as_view(), name="netappqtree"),
    path("qtree/<int:pk>/edit/", views.QTreeEditView.as_view(), name="netappqtree_edit"),
    path("qtree/<int:pk>/delete/", views.QTreeDeleteView.as_view(), name="netappqtree_delete"),
    path("qtree/delete/", views.QTreeBulkDeleteView.as_view(), name="netappqtree_bulk_delete"),
    path(
        "qtree/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="netappqtree_changelog",
        kwargs={"model": models.NetAppQTree},
    ),

    path("quota/", views.QuotaListView.as_view(), name="netappquota_list"),
    path("quota/add/", views.QuotaEditView.as_view(), name="netappquota_add"),
    path("quota/import/", views.QuotaImportView.as_view(), name="netappquota_import"),
    path("quota/<int:pk>/", views.QuotaView.as_view(), name="netappquota"),
    path("quota/<int:pk>/edit/", views.QuotaEditView.as_view(), name="netappquota_edit"),
    path("quota/<int:pk>/delete/", views.QuotaDeleteView.as_view(), name="netappquota_delete"),
    path("quota/delete/", views.QuotaBulkDeleteView.as_view(), name="netappquota_bulk_delete"),
    path(
        "quota/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="netappquota_changelog",
        kwargs={"model": models.NetAppQuota},
    ),

    path("lun/", views.LUNListView.as_view(), name="netapplun_list"),
    path("lun/add/", views.LUNEditView.as_view(), name="netapplun_add"),
    path("lun/import/", views.LUNImportView.as_view(), name="netapplun_import"),
    path("lun/<int:pk>/", views.LUNView.as_view(), name="netapplun"),
    path("lun/<int:pk>/edit/", views.LUNEditView.as_view(), name="netapplun_edit"),
    path("lun/<int:pk>/delete/", views.LUNDeleteView.as_view(), name="netapplun_delete"),
    path("lun/delete/", views.LUNBulkDeleteView.as_view(), name="netapplun_bulk_delete"),
    path(
        "lun/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="netapplun_changelog",
        kwargs={"model": models.NetAppLUN},
    ),
)
