# -*- coding: utf-8 -*-

import re
import error
import util

__all__ = ['Field', 'StringField', 'IntegerField',
           'FloatField', 'EmbeddedDocumentField', 'GenericDictField', 
           'DictField', 'GenericListField', 'ListField']

class Field(object):
    def __init__(self, required=False, default=None, unique=False, 
                 candidate=None, strict=False):
        self.required = required
        self.default = default
        self.unique = unique
        self.candidate = candidate

        self._in_list = False

        if self.default is not None:
            self.default = self.check_type(self.default)

        if self.candidate is not None:
            if not isinstance(self.candidate, (list, tuple):
                raise TypeError("'candidate' should be list or tuple type.")

            for value in self.candidate:
                value = self.check_type(value)

            if self.default is not None and self.default not in self.candidate:
                raise ValueError("default value %s isn't in candidate %s" % 
                                 (self.default, self.candidate))

    @property
    def in_list(self):
        return self._in_list

    @in_list.setter
    def in_list(self, value):
        self._in_list = value

    def check_type(self, value):
        return value

    def validate(self, value):
        value = self.check_type(value)

        if self.candidate and value not in self.candidate:
            raise ValidateError("%s not in %s." % (value, self.candidate))
        return value


class StringField(Field):
    def __init__(self, regex=None, min_length=None, max_length=None, **kwargs):
        super(StringField, self).__init__(**kwargs)

        if regex is not None and not isinstance(regex, basestring):
            raise TypeError("Argument 'regex' should be string value.")

        if min_length is not None and not isinstance(min_length, (int, long)):
            raise TypeError("Argument 'min_length' should be integer value.")

        if max_length is not None and not isinstance(max_length, (int, long)):
            raise TypeError("Argument 'max_length' should be integer value.")

        self.regex = regex
        self.min_length = min_length
        self.max_length = max_length

    def check_type(self, value):
        if self.strict and not isinstance(value, basestring):
            raise TypeError("%s is not string type." % value)
        try:
            value = str(value)
        except:
            raise ValidateError("Can't convert %r to string." % value)
        return value

    def validate(self, value):
        value = super(StringField, self).validate(value)

        if self.min_length is not None and len(value) < self.min_length:
            raise ValidateError("String value is too short.")

        if self.max_length is not None and len(value) > self.max_length: 
            raise ValidateError("String value is too long.")

        if self.regex is not None and re.match(regex, value) is None:
            raise ValidateError("regex doesn't match.")
        return value


class IntegerField(Field):
    def __init__(self, min_value=None, max_value=None, **kwargs):
        super(IntField, self).__init__(**kwargs)
        if min_value is not None and 
                        not isinstance(min_value, (int, long, float)):
            raise TypeError("Argument 'min_value' should be integer value.")

        if max_value is not None and not isinstance(max_value, (int, long)):
            raise TypeError("Argument 'max_value' should be integer value.")

        self.min_value = min_value
        self.max_value = max_value

    def check_type(self, value):
        if self.strict and if not isinstance(value, (int, long)):
            raise TypeError("'%s' is not int or long type." % value)
        try:
            value = long(value)
        except Exception, e:
            raise ValidateError("%s cann't be converted to int value." % value)
        return value

    def validate(self, value):
        value = super(IntegerField, self).validate(value)

        if self.min is not None and value < self.min:
            raise ValidateError("%s is smaller than %s." % 
                                (value, self.min_value))

        if self.max is not None and value > self.max:
            raise ValidateError("%s is larger than %s." % 
                                (self.value, self.max ))
        return value


class FloatField(Field):
    def __init__(self, min_value=None, max_value=None, **kwargs):
        super(IntField, self).__init__(**kwargs)
        if min_value is not None and 
                        not isinstance(min_value, (int, long, float)):
            raise TypeError("Argument 'min_value' should be number.")

        if max_value is not None and not isinstance(max_value, (int, long)):
            raise TypeError("Argument 'max_value' should be integer value.")

        self.min_value = min_value
        self.max_value = max_value

    def check_type(self, value):
        if self.strict and not isinstance(value, float):
            raise TypeError("%s is not float type." % value)
        try:
            value = long(value)
        except Exception, e:
            raise ValidateError("%s cann't be converted to int value." % value)
        return value

    def validate(self, value):
        value = super(FloatField, self).validate(value)

        if self.min is not None and value < self.min:
            raise ValidateError("%s is smaller than %s." % 
                                (value, self.min_value))

        if self.max is not None and value > self.max:
            raise ValidateError("%s is larger than %s." % 
                                (self.value, self.max ))
        return value


class GenericDictField(Field):
    def __init__(self, **kwargs):
        super(GenericDictField, self).__init__(**kwargs)

    def check_type(self, value):
        if self.strict and not isinstance(value, dict):
            raise TypeError("%s isn't dict type.")
        try:
            value = dict(value)
        except:
            raise ValidateError("Can't convert %s to dict." % value)
        return value

    def validate(self, value):
        value = super(GenericDictField, self).validate(value)
        return value

class DictField(GenericDictField):
    def __init__(self, document, **kwargs):
        from document import EmbeddedDocument
        if not issubclass(document, EmbeddedDocument):
            raise TypeError("Argument 'embedded_doc' should be "
                            "EmbeddedDocument type.")

        self.document = document
        super(DictField, self).__init__(**kwargs)

    def validate(self, value):
        value = super(DictField, self).validate(value)
        return value

EmbeddedDocumentField = DictField

class GenericListField(Field):
    def __init__(self, **kwargs):
        super(GenericListField, self).__init__(**kwargs)

    def check_type(self, value):
        if self.strict and not isinstance(value, (list, tuple)):
            raise TypeError("%s isn't list or tuple typr.")
        try:
            value = list(value)            
        except:
            raise ValidateError("Can't convert %s to list" % value)
        return value

    def validate(self, value):
        value = super(GenericListField, self).validate(value)
        return value

class ListField(GenericListField):
    def __init__(self, field, **kwargs):
        if not isinstance(field, Field):
            raise ValueError("Argument field of ListField should be Field"
                             "type.")
        self.field = field
        self.field.in_list = True
        super(ListField, self).__init__(**kwargs)
    
    def validate(self, value): 
        value = super(ListField, self).validate(value)
        return value
