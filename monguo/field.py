# -*- coding: utf-8 -*-

import error
import util

__all__ = ['Field', 'StringField', 'NumberField', 'IntegerField', 
           'FloatField', 'EmbeddedDocumentField', 'GenericDictField', 
           'DictField', 'GenericListField', 'ListField']

class Field(object):
    def __init__(self, required=False, default=None, unique=False, 
                 candidate=None):
        self.required = required
        self.default = default
        self.unique = unique
        self.candidate = candidate

        self._in_list = False

        if self.default is not None:
            self.validate(self.default)

        if self.candidate is not None:
            if not (isinstance(self.candidate, tuple) or 
                    isinstance(self.candidate, list)):
                raise TypeError('candidate should be a list.')

            for item in self.candidate:
                self.validate(item)

    def validate(self, value):
        return value

    @property
    def in_list(self):
        return self._in_list

    @in_list.setter
    def in_list(self, value):
        self._in_list = value

class StringField(Field):
    def __init__(self, **kwargs):
        super(StringField, self).__init__(**kwargs)

    def validate(self, value):
        return value

class NumberField(Field):
    def __init__(self, **kwargs):
        super(NumberField, self).__init__(**kwargs)

    def validate(value):
        try:
            value = float(value)
        except:
            raise ValueError("Value of NumberField must be a number.")

        return value

class IntegerField(NumberField):
    def __init__(self, **kwargs):
        super(IntegerField, self).__init__(**kwargs)

    def validate(self, value):
        return value

class FloatField(NumberField):
    def __init__(self, **kwargs):
        super(IntegerField, self).__init__(**kwargs)

    def validate(self, value):
        return value

class GenericDictField(Field):
    def __init__(self, **kwargs):
        super(GenericDictField, self).__init__(**kwargs)

    def validate(self, value):
        return value

class DictField(Field):
    def __init__(self, document, **kwargs):
        from document import EmbeddedDocument
        if not issubclass(document, EmbeddedDocument):
            raise TypeError("Argument 'embedded_doc' should be "
                            "EmbeddedDocument type.")

        self.document = document
        super(DictField, self).__init__(**kwargs)

    def validate(self, value):
        if not isinstance(value, dict):
            raise TypeError('not dict')
        return value

EmbeddedDocumentField = DictField

class GenericListField(Field):
    def __init__(self, **kwargs):
        super(GenericListField, self).__init__(**kwargs)

    def validate(self, value):
        return value

class ListField(Field):
    def __init__(self, field, **kwargs):
        if not isinstance(field, Field):
            raise ValueError("Argument field of ListField should be Field"
                             "type.")
        self.field = field
        self.field.in_list = True
        super(ListField, self).__init__(**kwargs)
    
    def validate(self, value): 
        return value
