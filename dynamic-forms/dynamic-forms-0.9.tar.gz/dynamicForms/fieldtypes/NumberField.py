from django.core.exceptions import ValidationError

from dynamicForms.fieldtypes import Field
from dynamicForms.fieldtypes import FieldFactory
from dynamicForms.statistics.NumericStatistics import NumericStatistics

class NumberField(Field.Field):
    """
    Number field type class.
    """
    template_name = "number/template.html"
    edit_template_name = "number/template_edit.html"
    prp_template_name = "number/properties.html"
    sts_template_name = "number/template_statistic.html"
    
    def check_min(self, value, **kwargs):
        field = kwargs['field']
        val = field.validations
        if ((val.min_number != None) and (int(value) < val.min_number)):
            raise ValidationError("Value below the minimum acceptable.")

    def check_max(self, value, **kwargs):
        field = kwargs['field']
        val = field.validations
        if ((val.max_number != None) and (int(value) > val.max_number)):
            raise ValidationError("Value above the maximum acceptable.")
        
    def int_check(self, value, **kwargs):
        try:
            int(value)
        except (ValueError, TypeError):
            print('except (ValueError, TypeError):')
            raise ValidationError('Enter a valid integer.', code='invalid')
        
    def get_methods(self, **kwargs):
        # Default validation or pass
        base = super(NumberField, self).get_methods(**kwargs)
        base.append(self.int_check)
        field = kwargs['field']
        restrictions = field.validations
        if (restrictions.min_number != None):
            base.append(self.check_min)
        if (restrictions.max_number != None):
            base.append(self.check_max)
        return base
    
    def check_consistency(self, field):
        # When a field is created check if the restrictions are consistent
        val = field.validations
        if not val.valid_number():
            raise ValidationError("The min value might not "
                "be below the max value.")
                
    def get_statistics(self, data, field):
        """
        Returns a serialized NumericStatistics data containing statistical 
        data for the field.
        """  
        statistics = super(NumberField, self).get_statistics(data, field)      
        numericStatistics = NumericStatistics(data)
        statistics.update(numericStatistics.getSerializedData())
        return statistics

    def get_assets():
        return ['js/fields/NumberField.js', 'js/operators/operatorNumber.js']

    def get_styles():
        return ['css/fields/NumberField.css']

    def __str__(self):
        return "NumberField"

FieldFactory.FieldFactory.register('NumberField', NumberField)
