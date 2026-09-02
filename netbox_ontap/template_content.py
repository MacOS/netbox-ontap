from netbox.plugins import PluginTemplateExtension
from django.db.models import Q, Sum
from django.template.defaultfilters import filesizeformat

from .models import NetAppLUN, NetAppQTree, NetAppQuota, NetAppSVM, NetAppVolume


class TenantStorageCard(PluginTemplateExtension):
	models = ["tenancy.tenant"]

	def right_page(self):
		tenant = self.context["object"]
		request = self.context["request"]
		svms = NetAppSVM.objects.restrict(request.user, "view").filter(tenant=tenant).distinct().order_by("name")

		# One-way expansion: direct SVM assignment includes all child objects.
		# A volume assigned to a tenant must not implicitly expose the whole SVM.
		volumes = (
			NetAppVolume.objects.restrict(request.user, "view")
			.filter(
				Q(tenant=tenant)
				| Q(svm__in=svms)
				| Q(ontap_luns__tenant=tenant)
			)
			.select_related("svm")
			.distinct()
			.order_by("name")
		)

		qtrees = NetAppQTree.objects.restrict(request.user, "view").filter(volume__in=volumes).distinct()

		luns = (
			NetAppLUN.objects.restrict(request.user, "view")
			.filter(
				Q(tenant=tenant)
				| Q(tenant__isnull=True, volume__tenant=tenant)
				| Q(tenant__isnull=True, volume__tenant__isnull=True, volume__svm__tenant=tenant)
			)
			.select_related("volume", "volume__svm", "qtree", "qtree__volume")
			.distinct()
			.order_by("name")
		)
		for lun in luns:
			lun.size_display = filesizeformat(lun.size) if lun.size else "-"
		total_lun_size = luns.aggregate(total=Sum("size"))["total"] or 0

		quotas = (
			NetAppQuota.objects.restrict(request.user, "view")
			.filter(Q(volume__in=volumes) | Q(qtree__in=qtrees))
			.select_related("volume", "qtree", "qtree__volume")
			.distinct()
			.order_by("volume__name", "qtree__name", "index")
		)
		for quota in quotas:
			quota.size_display = "Metering quota" if quota.space_hard_limit is None else filesizeformat(quota.space_hard_limit)
		total_quota_size = quotas.aggregate(total=Sum("space_hard_limit"))["total"] or 0

		return self.render(
			"netbox_ontap/extends/tenant_storage.html",
			extra_context={
				"svms": svms,
				"volumes": volumes,
				"luns": luns,
				"total_lun_size": total_lun_size,
				"quotas": quotas,
				"total_quota_size": total_quota_size,
			},
		)


template_extensions = [TenantStorageCard]
