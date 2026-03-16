from netbox.plugins import PluginTemplateExtension
from django.db.models import Q, Sum
from django.template.defaultfilters import filesizeformat

from .models import LUN, QTree, Quota, SVM, Volume


class ClusterStorageCard(PluginTemplateExtension):
	models = ["virtualization.cluster"]

	def right_page(self):
		cluster = self.context["object"]

		# Only render, if it is an NetApp Cluster
		if cluster.type.id == 3 or cluster.type.id == "3":
			return ""
		
		svms = SVM.objects.filter(cluster=cluster).order_by("name")[:25]
		volumes = Volume.objects.filter(svm__cluster=cluster).order_by("name")[:25]
		luns = LUN.objects.filter(volume__svm__cluster=cluster).order_by("name")[:25]

		return self.render(
			"netbox_ontap/extends/cluster_storage.html",
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
		svms = SVM.objects.filter(tenant=tenant).distinct().order_by("name")

		# One-way expansion: direct SVM assignment includes all child objects.
		# A volume assigned to a tenant must not implicitly expose the whole SVM.
		volumes = (
			Volume.objects.filter(
				Q(tenant=tenant)
				| Q(svm__in=svms)
				| Q(ontap_luns__tenant=tenant)
			)
			.select_related("svm")
			.distinct()
			.order_by("name")
		)

		qtrees = QTree.objects.filter(volume__in=volumes).distinct()

		luns = (
			LUN.objects.filter(
				Q(tenant=tenant)
				| Q(volume__in=volumes)
				| Q(qtree__in=qtrees)
			)
			.select_related("volume", "volume__svm", "qtree", "qtree__volume")
			.distinct()
			.order_by("name")
		)
		for lun in luns:
			lun.size_display = filesizeformat(lun.size) if lun.size else "-"
		total_lun_size = luns.aggregate(total=Sum("size"))["total"] or 0

		quotas = (
			Quota.objects.filter(Q(volume__in=volumes) | Q(qtree__in=qtrees))
			.select_related("volume", "qtree", "qtree__volume")
			.distinct()
			.order_by("volume__name", "qtree__name", "index")
		)
		for quota in quotas:
			quota.size_display = filesizeformat(quota.size) if quota.size else "-"
		total_quota_size = quotas.aggregate(total=Sum("size"))["total"] or 0

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


template_extensions = [ClusterStorageCard, TenantStorageCard]
