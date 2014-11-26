from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.dispatch import receiver
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.views.generic import TemplateView
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.conf import settings
from django.template import RequestContext
from django.utils.decorators import method_decorator
from datetime import datetime
import json
import logging
import csv

from rest_framework.decorators import api_view,parser_classes
from rest_framework.parsers import MultiPartParser,FormParser,JSONParser
from rest_framework import generics
from rest_framework import permissions
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from io import BytesIO


from .models import Form, FormEntry, Version, FieldEntry, FileEntry
from .fields import PUBLISHED, DRAFT
from .serializers import FormSerializer, VersionSerializer
from .serializers import FieldEntrySerializer, FormEntrySerializer
from .fields import Field_Data
from .fieldtypes.FieldFactory import FieldFactory as Factory
from .fieldtypes.ModelField import ModelField
from .JSONSerializers import FieldSerializer, AfterSubmitSerializer 
from .statistics.StatisticsCtrl import StatisticsCtrl 
from dynamicForms.statistics.StatisticsPdf import StatisticsPdf 
from .signals import modified_logic



class FormList(generics.ListCreateAPIView):
    """
    APIView where the forms of the app are listed and a new form can be added.
    """
    model = Form
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def pre_save(self, obj):
        obj.owner = self.request.user

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FormList, self).dispatch(*args, **kwargs)

    def get(self, request):
        forms = Form.objects.values()
        index = 1

        for f in forms:
            # Obtain the list of versions of the form f
            # ordered by version number (descendant)
            query_set = Form.objects.get(slug=f['slug']).versions.order_by('number').reverse()
            vers_dict = query_set.values()
            # Assign the dict of versions to the form dict
            f["versions"] = vers_dict
            f["index"] = index
            f["username"] = User.objects.get(id=f['owner_id'])

            index += 1
            # Get the status of the last version,
            # to know if there is already a draft in this form
            if len(vers_dict) > 0:
                last_version = vers_dict[0]
                f["lastStatus"] = last_version['status']
        return render_to_response('mainPage.html', {"formList": forms}, context_instance=RequestContext(request))

@login_required
@api_view(['GET'])
def ordered_forms(request, order="id", ad="asc"):
    """
    Gets the list of all forms and versions from the database,
    and renders the template to show them
    """
    if order == "owner":
        f1 = Form.objects.all().order_by('owner__username')
    else:
        f1 = Form.objects.all().order_by(order)
    if (ad == 'dsc'):
        f1 = f1.reverse()
    forms = f1.values()
    index = 1
    for f in forms:
        # Obtain the list of versions of the form f
        # ordered by version number (descendant)
        query_set = Form.objects.get(slug=f['slug']).versions.order_by('number').reverse()
        vers_dict = query_set.values()
        # Assign the dict of versions to the form dict
        f["versions"] = vers_dict
        f["index"] = index
        f["username"] = User.objects.get(id=f['owner_id'])

        index += 1
        # Get the status of the last version,
        # to know if there is already a draft in this form
        if len(vers_dict) > 0:
            last_version = vers_dict[0]
            f["lastStatus"] = last_version['status']

    return render_to_response('mainPage.html', {"formList": forms}, context_instance=RequestContext(request))


class FormDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    APIView to see details, modify or delete a form.
    """
    queryset = Form.objects.all()
    serializer_class = FormSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def pre_save(self, obj):
        obj.owner = self.request.user

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(FormDetail, self).dispatch(*args, **kwargs)

class VersionList(generics.ListCreateAPIView):
    """
    APIView where the version of the selected form are listed
    and a new version can be added.
    """
    model = Version
    serializer_class = VersionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(VersionList, self).dispatch(*args, **kwargs)
    
    def get(self, request, pk, format=None):
        try:
            versions = Form.objects.get(id=pk).versions.all()
            serializer = VersionSerializer(versions, many=True)
            return Response(serializer.data)
        except Form.DoesNotExist:
            content = {"error": "There is no form with that slug"}
            return Response(content, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, pk, format=None):
        serializer = VersionSerializer(data=request.DATA)
        form = Form.objects.get(id=pk)
        if serializer.is_valid():
            serializer.object.form = form
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VersionDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    APIView to see details, modify or delete a version.
    """
    queryset = Version.objects.all()
    serializer_class = VersionSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(VersionDetail, self).dispatch(*args, **kwargs)
    
    def get_object(self, pk, number):
        try:
            form = Form.objects.get(id=pk)
            return form.versions.get(number=number)
        except ObjectDoesNotExist:
            content = {"error": "There is no form with that slug or the"
            " corresponding form has no version with that number"}
            return Response(content, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk, number, format=None):
        version = self.get_object(pk, number)
        serializer = VersionSerializer(version)
        return Response(serializer.data)

    def put(self, request, pk, number, format=None):
        version = self.get_object(pk, number)
        serializer = VersionSerializer(version, data=request.DATA)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, number, format=None):
        # Get related form of the version that is going to be deleted
        try:
            form = Form.objects.get(id=pk)
            # Get version
            version = Version.objects.get(form=form, number=number)
            # Only draft versions can be deleted this way
            if version.status == DRAFT:
                # If selected form has only a draft and no previous versions
                if len(Version.objects.filter(form=form)) == 1:
                    form.delete()
                else:
                    version.delete()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        except Form.DoesNotExist or Version.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class NewVersion(generics.CreateAPIView):
    """
    APIView to create a new version of a form or duplicate a form
    """
    permission_classes = (permissions.IsAuthenticated,)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(NewVersion, self).dispatch(*args, **kwargs)
    
    def get(self, request, pk, number, action):
        try:
            # Get version of form that is going to be duplicated-
            form = Form.objects.get(id=pk)
            version = Version.objects.get(form=form, number=number)
        except Version.DoesNotExist or Form.DoesNotExist:
            content = {"error": "There is no form with that slug or the"
            " corresponding form has no version with that number"}
            return Response(content, status=status.HTTP_404_NOT_FOUND)
        # If action new version
        if action == "new":
            # Create version and save it on database
            new_version = Version(json=version.json, form=form)
            new_version.save()
        # If action duplicate a version
        elif action == "duplicate":
            # Create a copy of the form related to selected version
            new_form = Form(title=form.title, owner=request.user)
            count = 2
            try:
                f_try = 1
                while (f_try != None):
                    suffix = "(" + str(count) + ")"
                    # New_form.title += str(count)
                    count += 1
                    f_try = Form.objects.filter(title=new_form.title + suffix).first()
            except Form.DoesNotExist:
                pass
            new_form.title += suffix
            new_form.save()
            # Create a copy of the version and save it on database
            new_version = Version(json=version.json, form=new_form)
            new_version.save()
        return HttpResponseRedirect(settings.FORMS_BASE_URL + "main/")


class DeleteVersion(generics.DestroyAPIView):
    """
    APIView to delete a form
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteVersion, self).dispatch(*args, **kwargs)
    
    def get(self, request, pk, number, format=None):
        # Get related form of the version that is going to be deleted
        try:
            form = Form.objects.get(id=pk)
            # Get version
            version = Version.objects.get(form=form, number=number)
            # Only draft versions can be deleted this way
            if version.status == DRAFT:
                # If selected form has only a draft and no previous versions
                if len(Version.objects.filter(form=form)) == 1:
                    form.delete()
                else:
                    version.delete()
                return HttpResponseRedirect(settings.FORMS_BASE_URL + "main/")
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        except Form.DoesNotExist or Version.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class DeleteForm(generics.DestroyAPIView):
    """
    APIView to delete a form
    """
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(DeleteForm, self).dispatch(*args, **kwargs)
    
    def get(self, request, pk):
        # Get form and delete it
        try:
            form = Form.objects.get(id=pk)
            form.delete()
            return HttpResponseRedirect(settings.FORMS_BASE_URL + "main/")
        except Form.DoesNotExist:
            return HttpResponseRedirect(settings.FORMS_BASE_URL + "chuck/")


class FillForm(generics.RetrieveUpdateDestroyAPIView):
    """
    APIView to retrieve current version of a form to be filled
    """
    serializer_class = VersionSerializer

    def get(self, request, slug, format=None):
        try:
            form_versions = Form.objects.get(slug=slug).versions.all()
            # We assume there is only one published version at any given time
            final_version = form_versions.filter(status=PUBLISHED).first()
            if (not final_version):
                error = {"error" : "This Form has not been published."}
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data=error)
            loaded = json.loads(final_version.json)
            for p in loaded['pages']:
                for f in p['fields']:
                    fld = (Factory.get_class(f['field_type']))()
                    if isinstance(fld, ModelField):
                        f['options'] = fld.find_options()
            final_version.json = json.dumps(loaded)
            serializer = VersionSerializer(final_version)
            return Response(serializer.data)
        except Form.DoesNotExist or Version.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, statusp, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, status=statusp, **kwargs)


def is_shown(request, version, field, item_id):
    logic = version.get_logic()

    # If field == True, we check for field logic, otherwise we check page logic
    if field:
        logic = logic['fields']
    else:
        logic = logic['pages']
    # If there are no logic restrictions to show the item,
    # item is always shown
    if item_id not in logic:
        return True

    eval_results = []
    conditions = logic[item_id]['conditions']
    for condition in conditions:
        data = ''
        form_json = json.loads(request.DATA['data'])
        for field in form_json:
            serializer = FieldEntrySerializer(data=field)
            if serializer.is_valid():
                if serializer.object.field_id == condition['field']:
                    field_org = serializer.object
                    data = field_org.answer
                    break
        operator = ''
        if condition['comparator'] == "greater_than":
            operator = '>'
        elif condition['comparator'] == "greater_than_or_equal":
            operator = '>='
        elif condition['comparator'] == "equal":
            operator = '=='
        elif condition['comparator'] == "not_equal":
            operator = '!='
        elif condition['comparator'] == "less_than_or_equal":
            operator = '<='
        elif condition['comparator'] == "less_than":
            operator = '<'
        if operator != '':
            expression = data + operator + condition['value'].__str__()
            eval_results.append(eval(expression))
        # TODO: Missing error handling
        else:
            pass

    if logic[item_id]['action'] == 'All':
        value = True
        for result in eval_results:
            value = value & result
    elif logic[item_id]['action'] == 'Any':
        value = False
        for result in eval_results:
            value = value | result
    if logic[item_id]['operation'] == 'Show':
        shown = value
    else:
        shown = not value

    return shown

def validate_logic(request, version):
    pages = version.get_pages()

    page_id = 0
    pages_show_value = []
    for page in pages:
        pages_show_value.append(is_shown(request, version, False, page_id.__str__()))
        page_id += 1

    form_json = json.loads(request.DATA['data'])
    for field in form_json:
        field_page = -1
        serializer = FieldEntrySerializer(data=field)
        if serializer.is_valid():
            obj = serializer.object
            index = -1
            for page in pages:
                index += 1
                for page_field in page['fields']:
                    if page_field['field_id'] == obj.field_id:
                        field_page = index
                        break
                if field_page != -1:
                    break
            # If field cannot be found, logic check fails
            if field_page == -1:
                return False

            shown = is_shown(request, version, True, obj.field_id.__str__())
            shown = shown & pages_show_value[field_page]
            if shown != obj.shown:
                # If recived shown value differs from calculated, we return False
                return False
    # If there are no errors, logic is valid
    return True

@api_view(['POST'])
@parser_classes((FormParser,MultiPartParser,JSONParser))
def submit_form_entry(request, slug, format=None):
    """
    APIView to submit a Form Entry.
    """
    error_log = {"error": ""}
    form_versions = Form.objects.get(slug=slug).versions.all()
    final_version = form_versions.filter(status=PUBLISHED).first()
    form_json = json.loads(request.DATA['data'])
    for field in form_json:
        serializer = FieldEntrySerializer(data=field)
        if serializer.is_valid():
            obj = serializer.object
            if obj.required and obj.answer.__str__() == '' and obj.shown:
                error_log['error'] += obj.text + ': This field is required\n'
            elif not obj.required and obj.answer.__str__() == '':
                pass
            elif obj.shown:
                fld = (Factory.get_class(obj.field_type))()
                try:
                    loaded = json.loads(final_version.json)
                    f_id = obj.field_id
                    kw = {}
                    f = Field_Data()
                    data = FieldSerializer(f, field)
                    if (data.is_valid()):
                        kw['field'] = f
                        kw['options'] = fld.get_options(loaded, f_id)
                        fld.validate(obj.answer, **kw)
                    else:
                        raise ValidationError("Invalid JSON format.")
                    
                except ValidationError as e:
                    error_log['error'] += e.message
        else:
            return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
    # Make sure logic contraints are respected.
    logic_check = validate_logic(request, final_version)
    if not logic_check:
        modified_logic.send(sender=request, sent_data=request.DATA['data'])
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
    if error_log['error'] != "":
        return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data=error_log)
    entry = FormEntry(version=final_version)
    entry.entry_time = datetime.now()
    entry.save()
    form_json = json.loads(request.DATA['data'])
    for field in form_json:
            serializer = FieldEntrySerializer(data=field)
            if serializer.is_valid():
                serializer.object.entry = entry
                if not serializer.object.shown:
                    serializer.object.answer = ''
                serializer.save()
                # If field is a FileField we find the corresponding file and save it to the database
                if serializer.object.field_type == 'FileField':
                    data_json = serializer.object.answer
                    if data_json != '':
                        FileEntry.objects.create(field_id=serializer.object.field_id,file_type=request.FILES[data_json].content_type,file_data=request.FILES[data_json],field_entry=FieldEntry.objects.get(pk=serializer.object.pk),file_name=request.FILES[data_json].name)
    return Response(status=status.HTTP_200_OK)

logger = logging.getLogger(__name__)

@receiver(modified_logic)
def modified_logic_handler(sender, **kwargs):
    logger.error("Submitted form logic has been modified. DATA:" + kwargs['sent_data'].__str__())

@login_required
@api_view(['GET'])
def get_responses(request, pk, number, format=None):
    """
    View to get all the entries for a particular form.
    """
    try:
        form = Form.objects.get(pk=pk)
        v = form.versions.get(number=number)
        if (v.status == DRAFT):
            content = {"error": "This version's status is Draft."}
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)
        queryset = v.entries.all()
        if queryset:
            serializer = FormEntrySerializer(queryset, many=True)
            return Response(serializer.data)
        else: 
            return Response(data="No field entries for this form", status=status.HTTP_406_NOT_ACCEPTABLE)
    except ObjectDoesNotExist:
        content = {"error": "There is no form with that slug or the"
        " corresponding form has no version with that number"}
        return Response(content, status=status.HTTP_404_NOT_FOUND)

@login_required
@api_view(['GET'])
def get_constants(request, format=None):
    """
    View to get the available field type IDs.
    """
    data = Factory.get_strings()
    return Response(status=status.HTTP_200_OK, data=data)

@login_required
@api_view(['GET'])
def get_URL(request, format=None):
    """
    View to get the base URL.
    """
    data = {'URL': settings.FORMS_BASE_URL}
    return Response(status=status.HTTP_200_OK, data=data)


class FieldTemplateView(TemplateView):
    """
    Renders the field type templates.
    """
    def get_template_names(self):
        field = Factory.get_class(self.kwargs.get('type'))
        return field().render()


class FieldEditTemplateView(TemplateView):
    """
    Renders the field type templates.
    """
    def get_template_names(self):
        field = Factory.get_class(self.kwargs.get('type'))
        return field().render_edit()


class FieldPrpTemplateView(TemplateView):
    """
    Renders the field type properties templates.
    """
    def get_template_names(self):
        if (self.kwargs.get('type') == 'default'):
            return 'fields/field_properties_base.html'
        field = Factory.get_class(self.kwargs.get('type'))
        return field().render_properties()


class FieldStsTemplateView(TemplateView):
    """
    Renders the field type statistics templates.
    """
    def get_template_names(self):
        field = Factory.get_class(self.kwargs.get('type'))
        return field().render_statistic()


class StatisticsView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    
    def get(self, request, pk, number, fieldId=None,filterType=None, filter=""):
        """
        Returns statistics for version (pk, number)
        """
        try:
            statistics = StatisticsCtrl().getStatistics(pk, number, fieldId, filterType, filter)
            return Response(data=statistics,status=status.HTTP_200_OK)
        except Exception as e:
            error_msg = str(e) 
            return Response(data=error_msg, status=status.HTTP_406_NOT_ACCEPTABLE)

@login_required
@api_view(['GET'])
def after_submit_message(request, slug):
    form_versions = Form.objects.get(slug=slug).versions.all()
    final_version = form_versions.filter(status=PUBLISHED).first()
    js = json.loads(final_version.json)
    serializer = AfterSubmitSerializer(data=js['after_submit'])
    if serializer.is_valid():
        d = serializer.object
        msj = d.message
    message = msj.split("\n")
    return render_to_response('form_submitted.html', {"message": message}, context_instance=RequestContext(request))

@login_required
@api_view(['GET'])
def export_csv(request, pk, number, format=None):
    """
    Function view for exporting responses of form version in csv format
    """
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="responses.csv"'
    # Create a csv writer object
    writer = csv.writer(response)
    
    try:
        # Get version
        form = Form.objects.get(pk=pk)
        version = form.versions.get(number=number)
        
        # Only from a not draft version a csv file can be exported
        if (version.status == DRAFT):
            content = {"error": "This version's status is Draft."}
            return Response(content, status=status.HTTP_406_NOT_ACCEPTABLE)

        # Get all entries
        formEntries = version.entries.all()
        if formEntries:
            initial = formEntries[0]
            labels = []
            for field in initial.fields.all().order_by("field_id"):
                labels.append('"' + field.text + '"')
            writer.writerow(labels)
            for formEntry in formEntries:
                fields = formEntry.fields.all().order_by("field_id")
                data = []
                for field in fields:
                    data.append(field.answer)
                writer.writerow(data)
            return response
        else: 
            return Response(data="No field entries for this form", status=status.HTTP_406_NOT_ACCEPTABLE)
    except ObjectDoesNotExist:
        content = {"error": "There is no form with that slug or the"
        " corresponding form has no version with that number"}
        return Response(content, status=status.HTTP_404_NOT_FOUND)
@login_required
@api_view(['GET'])
def export_pdf(request, pk, number, field):
    """
    View for exporting field statistics on pdf format
    """
    try:
        
        statistics = StatisticsCtrl().getFieldStatistics(pk, number, field)
        
        #Create the HttpResponse object with the appropriate PDF headers.
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="field_statistics.pdf"'
        
        buffer = BytesIO()
         
        report = StatisticsPdf(buffer, 'A4', statistics)
        pdf = report.print_statistics() 
        
        response.write(pdf)
        
        return response
    
    except Exception as e:
        error_msg = str(e) 
    return Response(data=error_msg, status=status.HTTP_406_NOT_ACCEPTABLE)

@api_view(['GET'])
def download_file(request,field_id,entry):
    
    fieldEntry = FieldEntry.objects.get(pk=entry)
    fileEntry = fieldEntry.files.get(field_id=field_id)       
    response = HttpResponse(fileEntry.file_data,content_type=fileEntry.file_type)
    response['Content-Disposition'] = 'attachment; filename="' + fileEntry.file_name+'"'
    return response

@api_view(['GET'])
def render_form(request, format=None, **kwargs):
    base_url = settings.FORMS_BASE_URL
    return render_to_response('visor.html', {"instance": kwargs['instance'], "base_url": base_url}, context_instance=RequestContext(request))
