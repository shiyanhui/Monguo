# -*- coding: utf-8 -*-

import inspect
import motor
import functools
from tornado import gen

from connection import collection
from field import *

def validate(monguo_cls, motor_method, has_write_concern):
	@classmethod
	@functools.wraps(motor_method)
	def method(cls, *args, **kwargs):
		return cls._collection.find_one()
	return method
		
class MonguoAttributeFactory(object):
	def __init__(self, has_write_concern):
		self.has_write_concern = has_write_concern

	def create_attribute(self, cls, attr_name):
		motor_method = getattr(cls.__delegate_class__, attr_name)
		return validate(cls, motor_method,self.has_write_concern)

class ReadAttribute(MonguoAttributeFactory):
	def __init__(self):
		super(ReadAttribute, self).__init__(has_write_concern=False)

class WriteAttribute(MonguoAttributeFactory):
	def __init__(self):
		super(WriteAttribute, self).__init__(has_write_concern=True)

class CommandAttribute(MonguoAttributeFactory):
	def __init__(self):
		super(CommandAttribute, self).__init__(has_write_concern=False)

class MonguoMetaClass(type):
	def __new__(cls, name, bases, attrs):
		new_class = type.__new__(cls, name, bases, attrs)
		if getattr(new_class, '__delegate_class__', None):
			for base in reversed(inspect.getmro(new_class)):
				for name, attr in base.__dict__.items():
					if isinstance(attr, MonguoAttributeFactory):
						new_attr = attr.create_attribute(new_class, name)
						setattr(new_class, name, new_attr)
		return new_class

class Document(object):
	__delegate_class__ = motor.Collection
	__metaclass__ = MonguoMetaClass

	_collection = collection

	create_index 	  = CommandAttribute()
	drop_indexes      = CommandAttribute()
	drop_index  	  = CommandAttribute()
	drop              = CommandAttribute()
	ensure_index      = CommandAttribute()
	reindex           = CommandAttribute()
	rename            = CommandAttribute()
	find_and_modify   = CommandAttribute()
	map_reduce        = CommandAttribute()
	update            = WriteAttribute()
	insert            = WriteAttribute()
	remove            = WriteAttribute()
	save              = WriteAttribute()
	index_information = ReadAttribute()
	count             = ReadAttribute()
	options           = ReadAttribute()
	group             = ReadAttribute()
	distinct          = ReadAttribute()
	inline_map_reduce = ReadAttribute()
	find_one          = ReadAttribute()
	aggregate         = ReadAttribute()
	uuid_subtype      = motor.ReadWriteProperty()
	full_name         = motor.ReadOnlyProperty()

	
