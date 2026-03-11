from django.urls import path

from netbox.views.generic import ObjectChangeLogView

from . import models, views


urlpatterns = (
    path("svm/", views.SVMListView.as_view(), name="svm_list"),
    path("svm/add/", views.SVMEditView.as_view(), name="svm_add"),
    path("svm/import/", views.SVMImportView.as_view(), name="svm_import"),
    path("svm/<int:pk>/", views.SVMView.as_view(), name="svm"),
    path("svm/<int:pk>/edit/", views.SVMEditView.as_view(), name="svm_edit"),
    path("svm/<int:pk>/delete/", views.SVMDeleteView.as_view(), name="svm_delete"),
    path("svm/delete/", views.SVMBulkDeleteView.as_view(), name="svm_bulk_delete"),
    path(
        "svm/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="svm_changelog",
        kwargs={"model": models.SVM},
    ),

    path("volume/", views.VolumeListView.as_view(), name="volume_list"),
    path("volume/add/", views.VolumeEditView.as_view(), name="volume_add"),
    path("volume/import/", views.VolumeImportView.as_view(), name="volume_import"),
    path("volume/<int:pk>/", views.VolumeView.as_view(), name="volume"),
    path("volume/<int:pk>/edit/", views.VolumeEditView.as_view(), name="volume_edit"),
    path("volume/<int:pk>/delete/", views.VolumeDeleteView.as_view(), name="volume_delete"),
    path("volume/delete/", views.VolumeBulkDeleteView.as_view(), name="volume_bulk_delete"),
    path(
        "volume/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="volume_changelog",
        kwargs={"model": models.Volume},
    ),

    path("qtree/", views.QTreeListView.as_view(), name="qtree_list"),
    path("qtree/add/", views.QTreeEditView.as_view(), name="qtree_add"),
    path("qtree/import/", views.QTreeImportView.as_view(), name="qtree_import"),
    path("qtree/<int:pk>/", views.QTreeView.as_view(), name="qtree"),
    path("qtree/<int:pk>/edit/", views.QTreeEditView.as_view(), name="qtree_edit"),
    path("qtree/<int:pk>/delete/", views.QTreeDeleteView.as_view(), name="qtree_delete"),
    path("qtree/delete/", views.QTreeBulkDeleteView.as_view(), name="qtree_bulk_delete"),
    path(
        "qtree/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="qtree_changelog",
        kwargs={"model": models.QTree},
    ),

    path("quota/", views.QuotaListView.as_view(), name="quota_list"),
    path("quota/add/", views.QuotaEditView.as_view(), name="quota_add"),
    path("quota/import/", views.QuotaImportView.as_view(), name="quota_import"),
    path("quota/<int:pk>/", views.QuotaView.as_view(), name="quota"),
    path("quota/<int:pk>/edit/", views.QuotaEditView.as_view(), name="quota_edit"),
    path("quota/<int:pk>/delete/", views.QuotaDeleteView.as_view(), name="quota_delete"),
    path("quota/delete/", views.QuotaBulkDeleteView.as_view(), name="quota_bulk_delete"),
    path(
        "quota/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="quota_changelog",
        kwargs={"model": models.Quota},
    ),

    path("lun/", views.LUNListView.as_view(), name="lun_list"),
    path("lun/add/", views.LUNEditView.as_view(), name="lun_add"),
    path("lun/import/", views.LUNImportView.as_view(), name="lun_import"),
    path("lun/<int:pk>/", views.LUNView.as_view(), name="lun"),
    path("lun/<int:pk>/edit/", views.LUNEditView.as_view(), name="lun_edit"),
    path("lun/<int:pk>/delete/", views.LUNDeleteView.as_view(), name="lun_delete"),
    path("lun/delete/", views.LUNBulkDeleteView.as_view(), name="lun_bulk_delete"),
    path(
        "lun/<int:pk>/changelog/",
        ObjectChangeLogView.as_view(),
        name="lun_changelog",
        kwargs={"model": models.LUN},
    ),
)
