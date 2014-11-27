"""Forms of the aps_bom app."""
from csv import DictReader

from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as __

from .models import BOM, BOMItem, CBOM, CBOMItem, EPN, IPN, Unit


class BaseUploadForm(forms.ModelForm):
    csv_file = forms.FileField()

    def append_error(self, error_message, field="__all__"):
        if field in self.errors:
            self.errors[field].append(error_message)
        else:
            self.errors[field] = [error_message]

    def clean(self):
        cleaned_data = super(BaseUploadForm, self).clean()
        # don't do anything with the file if there are errors already
        if any(self.errors):
            return cleaned_data

        if self.Meta.model == CBOM:
            self.company = self.cleaned_data['customer']

        # initiate the csv dictreader with the uploaded file
        temp_csv_file = self.files.get('csv_file')
        with open(temp_csv_file.temporary_file_path(), 'rU') as csv_file:
            self.reader = DictReader(csv_file)
            self.clean_lines()

        return cleaned_data

    def clean_lines(self):
        # update the fieldnames to match the ones on the model
        new_names = []
        for fieldname in self.reader.fieldnames:
            new_names.append(fieldname.lower())
        self.reader.fieldnames = new_names

        # iterate over the lines and clean the values
        self.clean_lines = []
        for line_dict in self.reader:
            for key, value in line_dict.iteritems():
                # strip blank spaces
                value = value.strip()
                line_dict[key] = value
                if key == 'consign':
                    if value == '0':
                        value = False
                    else:
                        value = True
                    line_dict[key] = value
                if key == 'ipn':
                    try:
                        ipn = IPN.objects.get(code=value)
                    except IPN.DoesNotExist:
                        this_link = (
                            '<a href="{0}" target="_blank">{0}</a>'.format(
                                reverse('admin:aps_bom_ipn_add')))
                        self.append_error(__(
                            'The ipn "{0}" does not exist.'
                            ' Please create it first. {1}'.format(
                                value, this_link)))
                    except IPN.MultipleObjectsReturned:
                        # TODO temporary workaround
                        self.append_error(__(
                            'There are multiple entries for the IPN "{0}".'
                            ' Please resolve this error before'
                            ' uploading.'.format(value)), field='ipn')
                    else:
                        line_dict[key] = ipn
                if key == 'unit':
                    try:
                        unit = Unit.objects.get(code=value)
                    except Unit.DoesNotExist:
                        this_link = (
                            '<a href="{0}" target="_blank">{0}</a>'.format(
                                reverse('admin:aps_bom_unit_add')))
                        self.append_error(__(
                            'The unit "{0}" does not exist.'
                            ' Please create it first. {1}'.format(
                                value, this_link)))
                    else:
                        line_dict[key] = unit
                if key == 'epn':
                    try:
                        epn = EPN.objects.get(epn=value, company=self.company)
                    except EPN.DoesNotExist:
                        epn = EPN.objects.create(
                            description=line_dict.get('description'),
                            epn=value, company=self.company)
                        this_link = (
                            '<a href="{0}" target="_blank">{0}</a>'.format(
                                reverse('admin:aps_bom_epn_change',
                                        args=(epn.id, ))))
                        self.append_error(__(
                            'The EPN "{0}" does not exist.'
                            ' Please visit {1} to update it and then'
                            ' re-upload the file.'.format(
                                value, this_link)))
                    else:
                        if epn.ipn is None or epn.cpn is None:
                            this_link = (
                                '<a href="{0}" target="_blank">{0}</a>'.format(
                                    reverse('admin:aps_bom_epn_change',
                                            args=(epn.id, ))))
                            self.append_error(__(
                                'The EPN "{0}" does not have all the'
                                ' required data.'
                                ' Please visit {1} to update it and then'
                                ' re-upload the file.'.format(
                                    value, this_link)))
                        else:
                            line_dict[key] = epn
                if key == 'shape':
                    pass
            line_dict.pop('description')
            if 'shape' in line_dict:
                line_dict.pop('shape')
            self.clean_lines.append(line_dict)
        return self.clean_lines


class BOMUploadForm(BaseUploadForm):
    """Custom ModelForm, that handles the upload for BOM.csv files."""

    def __init__(self, *args, **kwargs):
        super(BOMUploadForm, self).__init__(*args, **kwargs)
        self.fields['ipn'].required = True

    def save(self):
        instance = super(BOMUploadForm, self).save()
        for bomitemdict in self.clean_lines:
            bomitemdict.update({'bom': instance})
            BOMItem.objects.create(**bomitemdict)
        return instance

    class Meta:
        model = BOM
        fields = ['description', 'ipn']


class CBOMUploadForm(BaseUploadForm):
    """Custom ModelForm, that handles the upload for cBOM.csv files."""

    def save(self):
        instance = super(CBOMUploadForm, self).save()
        for cbomitemdict in self.clean_lines:
            cbomitemdict.update({'bom': instance})
            CBOMItem.objects.create(**cbomitemdict)
        return instance

    class Meta:
        model = CBOM
        fields = [
            'customer', 'description', 'html_link', 'product', 'version_date']
