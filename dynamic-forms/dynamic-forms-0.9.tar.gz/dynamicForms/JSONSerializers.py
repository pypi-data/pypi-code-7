from rest_framework import serializers
import ast

from dynamicForms.fields import Validations, Dependencies, Field_Data, Option, AfterSubmit

class ValidationSerializer(serializers.Serializer):
    """
    Serializer for the validations in the versions json
    """
    max_len_text = serializers.IntegerField(required=False)
    max_number = serializers.IntegerField(required=False)
    min_number = serializers.IntegerField(required=False)
        
    def restore_object(self, attrs, instance=None):
        """
        Given a dictionary of deserialized field values, either update
        an existing model instance, or create a new model instance.
        """
        if instance is not None:
            if not attrs.get('max_len_text') and (attrs.get('max_len_text') != 0):
                instance.max_len_text = None
            else:
                instance.max_len_text = attrs.get('max_len_text', instance.max_len_text)
            if not attrs.get('max_number') and (attrs.get('max_number') != 0):
                instance.max_number = None
            else:    
                instance.max_number = attrs.get('max_number', instance.max_number)
            if not attrs.get('min_number') and (attrs.get('min_number') != 0):
                instance.min_number = None
            else:
                instance.min_number = attrs.get('min_number', instance.min_number)
            return instance
        return Validations(**attrs)
    

class OptionSerializer(serializers.Serializer):
    label = serializers.CharField(max_length=100, required=False)
    id = serializers.IntegerField(required=False)
    
    def restore_object(self, attrs, instance=None):
        """
        Given a dictionary of deserialized field values, either update
        an existing model instance, or create a new model instance.
        """
        if instance is not None:
            instance.label = attrs.get('label', instance.label)
            instance.id = attrs.get('id', instance.id)
            return instance
        else:
            opt = Option()
            opt.label = attrs.get('label', opt.label)
            opt.id = attrs.get('id')
            return opt
    

class DependencySerializer(serializers.Serializer):
    pages = serializers.CharField(required=False)
    fields = serializers.CharField(required=False)
    
    def restore_object(self, attrs, instance=None):
        """
        Given a dictionary of deserialized field values, either update
        an existing model instance, or create a new model instance.
        """
        if instance is not None:
            instance.fields = ast.literal_eval(attrs.get('fields', instance.fields))
            instance.pages = ast.literal_eval(attrs.get('pages', instance.pages))
            return instance
        return Dependencies(**attrs)

        
class FieldSerializer(serializers.Serializer):
    text = serializers.CharField(required=True, max_length=500)
    required = serializers.BooleanField(required=True)
    tooltip = serializers.CharField(required=False, max_length=300)
    answer = serializers.CharField(required=False)
    options = OptionSerializer(many=True, required=False, allow_add_remove=True, read_only=False)
    dependencies = DependencySerializer(required=False)
    validations = ValidationSerializer(required=False)
    max_id = serializers.IntegerField(required=False)
    field_type = serializers.CharField(required=True, max_length=30)
    field_id = serializers.IntegerField(required=True)

    def restore_object(self, attrs, instance=None):
        """
        Given a dictionary of deserialized field values, either update
        an existing model instance, or create a new model instance.
        """
        if instance is not None:
            instance.text = attrs.get('text', instance.text)
            instance.required = attrs.get('required', instance.required)
            instance.tooltip = attrs.get('tooltip', instance.tooltip)
            instance.answer = attrs.get('answer', instance.answer)
            instance.options = attrs.get('options', instance.options)
            instance.max_id = attrs.get('max_id', instance.max_id)
            instance.field_type = attrs.get('field_type', instance.field_type)
            instance.field_id = attrs.get('field_id', instance.field_id)

            return instance
        return Field_Data(**attrs)


class AfterSubmitSerializer(serializers.Serializer):
    """
    Serializer for the validations in the versions json
    """
    sendMail = serializers.BooleanField(required=True)
    action = serializers.CharField(required=True)
    mailSubject = serializers.CharField(required=False)
    mailText = serializers.CharField(required=False)
    mailSender = serializers.CharField(required=False)
    mailRecipient = serializers.CharField(required=False)
    message = serializers.CharField(required=False)
    redirect = serializers.CharField(required=False)
    
    def restore_object(self, attrs, instance=None):
        """
        Given a dictionary of deserialized field values, either update
        an existing model instance, or create a new model instance.
        """
        if instance is not None:
            instance.sendMail = attrs.get('sendMail', instance.sendMail)
            instance.action = attrs.get('action', instance.action)
            instance.mailSubject = attrs.get('mailSubject', instance.mailSubject)
            instance.mailText = attrs.get('mailText', instance.mailText)
            instance.mailSender = attrs.get('mailSender', instance.mailSender)
            instance.mailRecipient = attrs.get('mailRecipient', instance.mailRecipient)
            instance.message = attrs.get('message', instance.message)
            instance.redirect = attrs.get('redirect', instance.redirect)
            return instance
        return AfterSubmit(**attrs)
