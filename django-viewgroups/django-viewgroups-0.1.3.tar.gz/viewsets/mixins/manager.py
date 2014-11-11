from copy import deepcopy
from django.core.urlresolvers import reverse
from viewsets.views import SearchMixin
import os

from viewsets.mixins.filter import FilterMixin
from viewsets.mixins.sort import SortMixin, TableMixin
from django.utils.functional import lazy


class ViewSetMixin(object):
    list_detail_link = "base:detail"
    title = None

    def get_title(self):
        if self.title:
           return self.title
        return self.name.replace("-", " ").title()

    def get_context_data(self, **kwargs):
        context = super(ViewSetMixin, self).get_context_data(**kwargs)
        if getattr(self, "manager", None):
            context.update(
                self.manager.extra_context(self.request, self),
                title=self.get_title()
            )
        return context

    # need to set the current app for url namespace resolution
    def render_to_response(self, context, **response_kwargs):
        if getattr(self, "manager", None):
            response_kwargs["current_app"] = self.manager.name
            context.update({"current_app": self.manager.name})

        return super(ViewSetMixin, self).render_to_response(context, **response_kwargs)

    def get_success_url(self):
        return reverse(self.manager.default_app + ":detail", args=[self.object.id],
            current_app=self.manager.name)

    def get_template_names(self):
        template_name = getattr(self, "template_name", None)
        if template_name:
            return template_name

        templates = [
            [
                self.manager.base_template_dir,
                self.manager.template_dir,
                self.name + ".html"
            ],
            [
                self.manager.base_template_dir,
                self.manager.default_app,
                self.name + ".html"
            ]
        ]

        if self.request.is_ajax():
            ajax_templates = deepcopy(templates)
            for template in ajax_templates:
                template[-1] = self.name + "_ajax.html"
            templates = ajax_templates + templates

        return [os.path.join(*bits) for bits in templates]

    def get_detail_link(self, obj):
        name = getattr(self, "list_detail_link")
        if name:
            return reverse(name, args=[obj.id], current_app=self.manager.name)
        return ""

    def get_list_display(self):
        ld = super(ViewSetMixin, self).get_list_display()
        if ld == TableMixin.list_display:
            ld2 = getattr(self.manager, "list_display", [])
            if ld2:
                ld = ld2
        return ld

    def get_list_display_links(self):
        return super(ViewSetMixin, self).get_list_display_links() or \
            getattr(self.manager, "list_display_links", ["__unicode__"])

    def get_list_filters(self):
        return super(ViewSetMixin, self).get_list_filters() or \
            getattr(self.manager, "list_filter", [])

    def get_search_fields(self):
        return super(ViewSetMixin, self).get_search_fields() or \
            getattr(self.manager, "search_fields", [])

    def get_actions(self):
        return super(ViewSetMixin, self).get_actions() or \
            getattr(self.manager, "actions", [])

    def get_queryset(self):
        qs = self.manager.get_queryset(self, self.request, **self.kwargs)
        if isinstance(self, FilterMixin):
            qs = self.get_filtered_queryset(qs)
        if isinstance(self, SearchMixin):
            qs = self.get_searched_queryset(qs)
        if isinstance(self, SortMixin):
            qs = self.get_sorted_queryset(qs)
        return qs
