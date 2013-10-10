# -*- coding: utf-8 -*-

import error

__all__ = ['Field', 'StringField']


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
        pass

class StringField(Field):
    def __init__(self, **kwargs):
        super(StringField, self).__init__(**kwargs)

    def validate(self, value):
        return value

class IntegerField(Field):
    def __init__(self, **kwargs):
        super(StringField, self).__init__(**kwargs)

    def validate(self, value):
        return value










