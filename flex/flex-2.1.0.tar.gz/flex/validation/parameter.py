import functools

from django.core.exceptions import ValidationError

from flex.utils import is_non_string_iterable
from flex.context_managers import ErrorCollection
from flex.validation.common import (
    generate_type_validator,
    generate_format_validator,
    generate_required_validator,
    generate_multiple_of_validator,
    generate_minimum_validator,
    generate_maximum_validator,
    generate_min_length_validator,
    generate_max_length_validator,
    generate_min_items_validator,
    generate_max_items_validator,
    generate_unique_items_validator,
    generate_pattern_validator,
    generate_enum_validator,
    validate_object,
    generate_value_processor,
)
from flex.validation.schema import (
    construct_schema_validators,
    generate_items_validator,
)
from flex.parameters import find_parameter
from flex.paths import path_to_regex
from flex.constants import EMPTY


def type_cast_parameters(parameter_values, parameter_definitions, context):
    typed_parameters = {}
    for key in parameter_values.keys():
        try:
            parameter_definition = find_parameter(parameter_definitions, name=key)
        except KeyError:
            continue
        value = parameter_values[key]
        value_processor = generate_value_processor(context=context, **parameter_definition)
        typed_parameters[key] = value_processor(value)
    return typed_parameters


def get_path_parameter_values(request_path, api_path, path_parameters, context):
    raw_values = path_to_regex(
        api_path,
        path_parameters,
    ).match(request_path).groupdict()
    return type_cast_parameters(raw_values, path_parameters, context=context)


def validate_path_parameters(request_path, api_path, path_parameters, context, inner=False):
    """
    Helper function for validating a request path
    """
    parameter_values = get_path_parameter_values(
        request_path, api_path, path_parameters, context,
    )
    validate_parameters(parameter_values, path_parameters, context=context, inner=inner)


def validate_query_parameters(raw_query_data, query_parameters, context, inner=False):
    query_data = {}
    for key, value in raw_query_data.items():
        if is_non_string_iterable(value) and len(value) == 1:
            query_data[key] = value[0]
        else:
            query_data[key] = value
    validate_parameters(query_data, query_parameters, context, inner=inner)


def validate_parameters(parameter_values, parameters, context, inner=False):
    validators = construct_multi_parameter_validators(parameters, context=context)

    with ErrorCollection(inner=inner) as errors:
        # we should have a validator for every parameter value
        assert not set(parameter_values.keys()).difference(validators.keys())

        for key, validator in validators.items():
            try:
                validator(parameter_values.get(key, EMPTY))
            except ValidationError as err:
                errors[key].extend(list(err.messages))


def construct_parameter_validators(parameter, context):
    """
    Constructs a dictionary of validator functions for the provided parameter
    definition.
    """
    validators = {}
    if 'schema' in parameter:
        validators.update(construct_schema_validators(parameter['schema'], context=context))
    for key in parameter:
        if key in validator_mapping:
            validators[key] = validator_mapping[key](context=context, **parameter)
    return validators


validator_mapping = {
    'type': generate_type_validator,
    'format': generate_format_validator,
    'required': generate_required_validator,
    'multipleOf': generate_multiple_of_validator,
    'minimum': generate_minimum_validator,
    'maximum': generate_maximum_validator,
    'minLength': generate_min_length_validator,
    'maxLength': generate_max_length_validator,
    'minItems': generate_min_items_validator,
    'maxItems': generate_max_items_validator,
    'uniqueItems': generate_unique_items_validator,
    'enum': generate_enum_validator,
    'pattern': generate_pattern_validator,
    'items': generate_items_validator,
}


def construct_multi_parameter_validators(parameters, context):
    """
    Given an iterable of parameters, returns a dictionary of validator
    functions for each parameter.  Note that this expects the parameters to be
    unique in their name value, and throws an error if this is not the case.
    """
    validators = {}
    for parameter in parameters:
        key = parameter['name']
        if key in validators:
            raise ValueError("Duplicate parameter name {0}".format(key))
        parameter_validators = construct_parameter_validators(parameter, context=context)
        validators[key] = functools.partial(
            validate_object,
            validators=parameter_validators,
            inner=True,
        )

    return validators
