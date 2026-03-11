from netbox.plugins import PluginTemplateExtension
from django.db.models import Q, Sum
from django.template.defaultfilters import filesizeformat

from .models import LUN, Quota, SVM, Volume


class ClusterStorageCard(PluginTemplateExtension):
	models = ["virtualization.cluster"]

	def right_page(self):
		cluster = self.context["object"]
		svms = SVM.objects.filter(cluster=cluster).order_by("name")[:25]
		volumes = Volume.objects.filter(svm__cluster=cluster).order_by("name")[:25]
		luns = LUN.objects.filter(volume__svm__cluster=cluster).order_by("name")[:25]

		return self.render(
			"netbox_storage/extends/cluster_storage.html",
			extra_context={
				"svms": svms,
				"volumes": volumes,
				"luns": luns,
			},
		)


class TenantStorageCard(PluginTemplateExtension):
	models = ["tenancy.tenant"]

	def right_page(self):
		tenant = self.context["object"]
		svms = SVM.objects.filter(tenant=tenant).order_by("name")
		volumes = (
			Volume.objects.filter(
				Q(tenant=tenant) |
				Q(svm__tenant=tenant)
			)
			.select_related("svm")
			.distinct()
			.order_by("name")
		)
		luns = (
			LUN.objects.filter(
				Q(tenant=tenant) |
				Q(volume__svm__tenant=tenant) |
				Q(volume__in=volumes) |
				Q(qtree__volume__in=volumes)
			)
			.select_related("volume", "volume__svm", "qtree", "qtree__volume")
			.distinct()
			.order_by("name")
		)
		quotas = (
			Quota.objects.filter(qtree__volume__in=volumes)
			.select_related("qtree", "qtree__volume")
			.distinct()
			.order_by("qtree__volume__name", "qtree__name", "index")
		)
		for quota in quotas:
			quota.size_display = filesizeformat(quota.size) if quota.size else "-"
		total_quota_size = quotas.aggregate(total=Sum("size"))["total"] or 0

		return self.render(
			"netbox_storage/extends/tenant_storage.html",
			extra_context={
				"svms": svms,
				"volumes": volumes,
				"luns": luns,
				"quotas": quotas,
				"total_quota_size": total_quota_size,
			},
		)


template_extensions = [ClusterStorageCard, TenantStorageCard]
