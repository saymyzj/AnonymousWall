from django.shortcuts import redirect


class WorkbenchRedirectAdminMixin:
    workbench_changelist_url = '/admin/'

    def get_model_perms(self, request):
        return {}

    def has_module_permission(self, request):
        return False

    def get_workbench_object_url(self, object_id):
        return self.workbench_changelist_url

    def changelist_view(self, request, extra_context=None):
        return redirect(self.workbench_changelist_url)

    def add_view(self, request, form_url='', extra_context=None):
        return redirect(self.workbench_changelist_url)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        return redirect(self.get_workbench_object_url(object_id))

    def delete_view(self, request, object_id, extra_context=None):
        return redirect(self.get_workbench_object_url(object_id))

    def history_view(self, request, object_id, extra_context=None):
        return redirect(self.get_workbench_object_url(object_id))
