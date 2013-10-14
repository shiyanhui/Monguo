# -*- coding: utf-8 -*-

import error

__all__ = ['Field', 'StringField', 'IntegerField', 'EmbeddedDocumentField', 
            'GenericDictField', 'DictField', 'GenericListField', 'ListField']

class Field(object):
    def __init__(self, required=False, default=None, 
                            unique=False, candidate=None):
        self.required = required
        self.default = default
        self.unique = unique
        self.candidate = candidate

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

class StringField(Field):
    def __init__(self, **kwargs):
        super(StringField, self).__init__(**kwargs)

    def validate(self, value):
        return value

class IntegerField(Field):
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
    def __init__(self, embedded_doc, **kwargs):
        from document import Document
        if not issubclass(embedded_doc, Document):
            raise TypeError("Argument 'embedded_doc' should be Document type.")

        self.embedded_doc = embedded_doc
        super(EmbeddedDocumentField, self).__init__(**kwargs)

    def validate(self, value):
        return value

EmbeddedDocumentField = DictField

class GenericListField(Field):
    def __init__(self, **kwargs):
        super(GenericListField, self).__init__(**kwargs)

    def validate(self, value):
        return value

class ListField(Field):
    def __init__(self, filed, **kwargs):
        super(ListField, self).__init__(**kwargs)
    
    def validate(self, value):        
        return value
