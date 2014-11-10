# coding=utf-8
from django import forms
from django.contrib.gis import forms as geoforms
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import FilteredSelectMultiple

from .models import DefaultLayerOption, ServiceOption, DatastoreOption, FieldOption, AccessFilterOption, ResourceOption, WidgetOption, MapContextOption, Resource

class GeoForm(geoforms.ModelForm):
     geom = geoforms.GeometryField(widget=geoforms.OSMWidget(attrs={
        'map_width': 1000,
        'map_height': 500,
        }))


class DefaultLayerOptionForm(forms.ModelForm):
    class Meta:
        model = DefaultLayerOption
        fields = '__all__'
        widgets = {
            'value': forms.Textarea(attrs={'rows': 1,}),
        }

class ServiceOptionForm(forms.ModelForm):
    class Meta:
        model = ServiceOption
        fields = '__all__'
        widgets = {
            'value': forms.Textarea(attrs={'rows': 1,}),
        }

class DatastoreOptionForm(forms.ModelForm):
    class Meta:
        model = DatastoreOption
        fields = '__all__'
        widgets = {
            'value': forms.Textarea(attrs={'rows': 1,}),
        }

class FieldOptionForm(forms.ModelForm):
    class Meta:
        model = FieldOption
        fields = '__all__'
        widgets = {
            'value': forms.Textarea(attrs={'rows': 1,}),
        }


class AccessFilterOptionForm(forms.ModelForm):
    class Meta:
        model = AccessFilterOption
        fields = '__all__'
        widgets = {
            'value': forms.Textarea(attrs={'rows': 1,}),
        }


class ResourceOptionForm(forms.ModelForm):
    class Meta:
        model = ResourceOption
        fields = '__all__'
        widgets = {
            'value': forms.Textarea(attrs={'rows': 1,}),
        }


class WidgetOptionForm(forms.ModelForm):
    class Meta:
        model = WidgetOption
        fields = '__all__'
        widgets = {
            'value': forms.Textarea(attrs={'rows': 1,}),
        }


class MapContextOptionForm(forms.ModelForm):
    class Meta:
        model = MapContextOption
        fields = '__all__'
        widgets = {
            'value': forms.Textarea(attrs={'rows': 1,}),
        }

#Pour ajouter "facilement" un many to many de l'autre côté du lien
class DatastoreForm(forms.ModelForm):
    fields = ('service', 'name', 'layers', 'resources', )
    resources = forms.ModelMultipleChoiceField(queryset=Resource.objects.all(),
        required=False, widget=FilteredSelectMultiple(
        _('resources'), False, attrs={'rows': '10'}))

    def __init__(self, *args, **kwargs):
        super(DatastoreForm, self).__init__(*args, **kwargs)
        if kwargs.get('instance'):
            self.fields['resources'].initial = self.instance.resource_set.all()

    def save(self, *args, **kwargs):
        super(DatastoreForm, self).save(*args, **kwargs)
        if hasattr(self.instance, 'resource_set'):
            self.instance.resource_set.clear()
        for resource in self.cleaned_data['resources']:
            Resource.datastores.through.objects.create(
                resource=resource, datastore=self.instance)
        return self.instance
