"""Views for the aps_bom app."""
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.views.generic import CreateView, TemplateView, View
from django.utils.decorators import method_decorator

from . import settings
from . import models
from .forms import BOMUploadForm, CBOMUploadForm


class DropDownChoicesAJAXView(View):
    """
    A view for returning drop down choices from certain criteria.

    """
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        action = self.request.GET.get('action')
        obj_id = self.request.GET.get('obj_id')
        if not request.is_ajax() or not hasattr(self, action):
            raise Http404
        return getattr(self, action)(obj_id)

    def get_epn_choices_for_customer(self, obj_id):
        choice_tempalte = '<option value="{value}">{label}</option>'
        choices = '<option value>---------</option>'
        for epn in models.EPN.objects.filter(company_id=obj_id):
            choices += choice_tempalte.format(value=epn.id, label=unicode(epn))
        return HttpResponse(choices)


class BOMUploadView(CreateView):
    """
    Lets a user upload a BOM.csv file and from it create a new BOM instance.

    """
    form_class = BOMUploadForm
    template_name = 'aps_bom/bom_upload.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(BOMUploadView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(BOMUploadView, self).get_form_kwargs()
        kwargs.update({'files': self.request.FILES})
        return kwargs

    def get_success_url(self):
        return settings.BOM_UPLOAD_SUCCESS_URL


class CBOMDownloadView(TemplateView):
    """
    View that displays a list of cBOMs and allows for downloading the cBOM
    or the BOM, that was generated from it.

    Allows choosing from a list of cBOMs.

    """
    template_name = 'aps_bom/cbom_download.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        self.cbom = None
        if kwargs.get('cbom_pk'):
            try:
                self.cbom = models.CBOM.objects.get(pk=kwargs.get('cbom_pk'))
            except models.CBOM.DoesNotExist:
                raise Http404
        return super(CBOMDownloadView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(CBOMDownloadView, self).get_context_data(**kwargs)
        if self.cbom is not None:
            ctx.update({
                'object': self.cbom,
                'bom': self.cbom.get_bom(),
                'bom_items': self.cbom.get_bom_items(),
                'cbom_file': self.cbom.get_csv_file(),
                'bom_file': self.cbom.get_bom_csv_file(),
            })
        ctx.update({
            'cboms': models.CBOM.objects.all(),
        })
        return ctx


class CBOMUploadView(CreateView):
    """
    Lets a user upload a cBOM.csv file and from it create a new CBOM instance.

    """
    form_class = CBOMUploadForm
    template_name = 'aps_bom/cbom_upload.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(CBOMUploadView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(CBOMUploadView, self).get_form_kwargs()
        kwargs.update({'files': self.request.FILES})
        return kwargs

    def get_success_url(self):
        return reverse('aps_bom_cbom_download', kwargs={
            'cbom_pk': self.object.pk})
