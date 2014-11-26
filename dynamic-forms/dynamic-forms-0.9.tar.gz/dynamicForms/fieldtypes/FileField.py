from django.core.exceptions import ValidationError

from dynamicForms.fieldtypes import Field
from dynamicForms.fieldtypes import FieldFactory


class FileField(Field.Field):
    """
    Text field validator, render and analize methods
    """
    template_name = "file/template.html"
    edit_template_name = "file/template_edit.html"
    prp_template_name = "file/properties.html"
    
    def get_assets():
        return ['js/fields/FileField.js']
    
    def __str__(self):
        return "FileField"


FieldFactory.FieldFactory.register('FileField', FileField)
