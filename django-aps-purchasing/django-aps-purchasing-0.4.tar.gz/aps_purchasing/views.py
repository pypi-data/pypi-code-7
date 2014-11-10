"""Views of the ``aps_purchasing`` app."""
from django.contrib.auth.decorators import login_required
from django.contrib.messages import info, warning
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, DetailView

from aps_bom.models import BOM

from .forms import QuotationUploadForm
from .models import Price, Quotation


class QuotationUploadView(CreateView):
    """View to upload a quotation and create Quotation items."""
    model = Quotation
    template_name = 'aps_purchasing/quotation_upload.html'
    form_class = QuotationUploadForm

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(QuotationUploadView, self).dispatch(
            request, *args, **kwargs)

    def get_success_url(self):
        info(self.request, _('Quotation successfully uploaded.'))
        return reverse('aps_purchasing_quotation_upload')


class ReportView(DetailView):
    """View to display prices and manufacturers belonging to a BOM."""
    template_name = 'aps_purchasing/report.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.object = None
        part_number = self.request.GET.get('part_number', '')
        if part_number:
            try:
                self.object = BOM.objects.get(ipn__code=part_number)
            except BOM.DoesNotExist:
                warning(request, _(
                    'BOM with part number "{0} not found".'.format(
                        part_number)))
            else:
                return redirect(reverse('aps_purchasing_report', kwargs={
                    'pk': self.object.pk}))
        else:
            try:
                self.object = BOM.objects.get(pk=kwargs.get('pk'))
            except BOM.DoesNotExist:
                pass
        return super(ReportView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(ReportView, self).get_context_data(**kwargs)
        if self.object is not None:
            prices = Price.objects.filter(
                quotation_item__mpn__DPNs__ipn__bomitems__bom=self.object)
            ctx.update({
                'prices': prices,
            })
        ctx.update({
            'boms': BOM.objects.all(),
        })
        return ctx

    def get_object(self, queryset=None):
        return self.object
