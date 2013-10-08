# -*- coding: utf-8 -*-

__all__ = ['Filed']

class Field(object):
    def __init__(
        self, required=True, default=None, unique=False, candidate=None):
    
        self.required  = required
        self.default   = default
        self.unique    = unique
        self.candidate = candidate
        self.value     = None

	def __get__(self, instance, owner):
		return self.value

	def __set__(self, instance, value):
        if self.validate(value):
            self.value = value

	def validate(self):
        pass


class StringField(Field):
    def __init__(self):
        pass

    def validate(self):
        pass