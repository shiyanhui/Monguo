# -*- coding: utf-8 -*-

__all__ = ['StringField']

class Field(object):
	def __get__(self, instance, owner):
		return None

	def __set__(self, instance, value):
		return None

class StringField(Field):
	print 'hello'

