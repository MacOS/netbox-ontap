from netbox.api.routers import NetBoxRouter
from . import views


app_name = 'netbox_storage'

router = NetBoxRouter()
router.register('svm', views.SVMViewSet)
router.register('volume', views.VolumeViewSet)
router.register('qtree', views.QTreeViewSet)
router.register('quota', views.QuotaViewSet)
router.register('lun', views.LUNViewSet)

urlpatterns = router.urls
