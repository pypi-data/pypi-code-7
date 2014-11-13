class ListWrapper(object):
    def __init__(self, instance, field):
        self.__instance = instance
        self.__field = field

    def __getitem__(self, item):
        if isinstance(item, slice):
            raise NotImplementedError

        wire_value = self.__instance._get_wire_values(self.__field.field_number)[item]

        final_value = self.__field._convert_to_final_type(wire_value.value)

        if hasattr(final_value, '_set_parent'):
            final_value._set_parent((self.__instance, self.__field.field_number, item))

        return final_value

    def __setitem__(self, key, value):
        if not self.__field._validate(value):
            raise ValueError

        self.__instance._set_wire_values(self.__field.field_number, self.__field.WIRE_TYPE,
                                         self.__field._convert_to_wire_type(value), key)

    def __len__(self):
        return len(self.__instance._get_wire_values(self.__field.field_number))

    def append(self, value):
        self.__instance._set_wire_values(self.__field.field_number, self.__field.WIRE_TYPE,
                                         self.__field._convert_to_wire_type(value), append=True)

    def insert(self, index, value):
        self.__instance._set_wire_values(self.__field.field_number, self.__field.WIRE_TYPE,
                                         self.__field._convert_to_wire_type(value), index=index,
                                         insert=True)
