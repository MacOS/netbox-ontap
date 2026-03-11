from netbox.plugins import PluginTemplateExtension

from .models import LUN, SVM, Volume


class ClusterStorageCard(PluginTemplateExtension):
	models = ["virtualization.cluster"]

	def right_page(self):
		cluster = self.context["object"]
		svms = SVM.objects.filter(cluster=cluster).order_by("name")[:25]
		volumes = Volume.objects.filter(svm__cluster=cluster).order_by("name")[:25]
		luns = LUN.objects.filter(svm__cluster=cluster).order_by("name")[:25]

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
		svms = SVM.objects.filter(tenant=tenant).order_by("name")[:25]
		volumes = Volume.objects.filter(tenant=tenant).order_by("name")[:25]
		luns = LUN.objects.filter(tenant=tenant).order_by("name")[:25]

		return self.render(
			"netbox_storage/extends/tenant_storage.html",
			extra_context={
				"svms": svms,
				"volumes": volumes,
				"luns": luns,
			},
		)


template_extensions = [ClusterStorageCard, TenantStorageCard]
