from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import json

from rest_framework import serializers

from dynamicForms.models import Form, FieldEntry, Version, FormEntry
from dynamicForms.fields import Field_Data
from dynamicForms.fieldtypes.FieldFactory import FieldFactory as Factory
from dynamicForms.JSONSerializers import FieldSerializer 


class FormSerializer(serializers.ModelSerializer):
    """
    Complete serializer for the forms used for the REST framework
    """
    owner = serializers.Field(source='owner.username')
    versions = serializers.RelatedField(many=True)

    class Meta:
        model = Form
        fields = ('id', 'title', 'slug', 'versions', 'owner')
        read_only_fields = ('slug', 'id', )


class VersionSerializer(serializers.ModelSerializer):
    """
    Complete serializer for the forms used for the REST framework
    """
    form = serializers.Field(source='form.title')
    json = serializers.CharField(required=False)

    def validate_json(self, attrs, source):
        value = json.loads(attrs[source])
        for page in value['pages']:
            for field in page['fields']:
                f_type = Factory.get_class(field['field_type'])
                kw = {}
                f = Field_Data()
                data = FieldSerializer(f, field)
                if (data.is_valid()):
                    f_type().check_consistency(f)
                else:
                    raise ValidationError("Invalid JSON format.")
        return attrs

    class Meta:
        model = Version
        fields = ('number', 'status', 'publish_date', 'expiry_date',
                 'json', 'form', 'captcha')
        read_only_fields = ('number',)


class UserSerializer(serializers.ModelSerializer):
    forms = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'forms')


class FieldEntrySerializer(serializers.ModelSerializer):

    class Meta:
        model = FieldEntry
        fields = ('field_id', 'field_type', 'text', 'required', 'shown', 'answer')


class FormEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for the form entries
    """
    fields = serializers.RelatedField(many=True)

    class Meta:
        model = FormEntry
        fields = ('entry_time', 'fields')
