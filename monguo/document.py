# -*- coding: utf-8 -*-

import inspect
import motor
import functools

import util

from tornado import gen

from connection import Connection
from error import *
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

class BaseDocument(object):
	meta = {}

	@classmethod
	def get_collection(cls):
		connection_name = cls.meta['connection'] if 'connection' in cls.meta
			else None
		db_name = cls.meta['db'] if 'db' in cls.meta else None 

		db = Connection.get_db(connection_name, db_name)
		if db is None:
			raise ConnectionError('mongodb not connected!')

		collection_name = cls.meta['collection'] if 'collection' in cls.meta
		 	else util.camel_to_underline(cls.__name__) 
		collection = db[collection_name]
		return collection

class Document(BaseDocument):
	__delegate_class__ = motor.Collection
	__metaclass__ = MonguoMetaClass

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

	

