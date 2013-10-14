# -*- coding: utf-8 -*-

import inspect
import motor
import functools
import types
import util

from tornado import gen
from bson.son import SON
from connection import Connection
from manipulator import MonguoSONManipulator
from error import *
from field import *

def bound_method(monguo_cls, motor_method, has_write_concern):
    @classmethod
    def method(cls, *args, **kwargs):
        
        options = {'args': args, 'kwargs': kwargs}
        collection = cls.get_collection()
        collection.database.add_son_manipulator(
                    MonguoSONManipulator(cls, motor_method, **options))

        new_method = getattr(collection, motor_method)

        if has_write_concern and motor_method == 'update':
            kwargs.update({'manipulate': True})
            return new_method(*args, **kwargs)
        return new_method(*args, **kwargs)
    return method

class MonguoAttributeFactory(object):
    def __init__(self, has_write_concern):
        self.has_write_concern = has_write_concern

    def create_attribute(self, cls, attr_name):
        return bound_method(cls, attr_name, self.has_write_concern)

class ReadAttribute(MonguoAttributeFactory):
    def __init__(self):
        super(ReadAttribute, self).__init__(has_write_concern=False)


class WriteAttribute(MonguoAttributeFactory):
    def __init__(self):
        super(WriteAttribute, self).__init__(has_write_concern=True)

class CommandAttribute(MonguoAttributeFactory):
    def __init__(self):
        super(CommandAttribute, self).__init__(has_write_concern=False)

class MonguoMeta(type):
    def __new__(cls, name, bases, attrs):
        new_class = type.__new__(cls, name, bases, attrs)

        delegate_class = getattr(new_class, '__delegate_class__', None)
        if delegate_class:
            if delegate_class == motor.Collection:
                for base in reversed(inspect.getmro(new_class)):
                    for name, attr in base.__dict__.items():
                        if isinstance(attr, Field):
                            if name.find('.') != -1 or name.find('$') != -1:
                                raise FieldNameError(field=name)

                        elif isinstance(attr, MonguoAttributeFactory):
                            new_attr = attr.create_attribute(new_class, name)
                            setattr(new_class, name, new_attr)

                        elif isinstance(attr, types.FunctionType):
                            new_attr = staticmethod(gen.coroutine(attr))
                            setattr(new_class, name, new_attr)
        return new_class


class BaseDocument(object):
    __delegate_class__ = motor.Collection
    __metaclass__      = MonguoMeta

    create_index      = CommandAttribute()
    drop_indexes      = CommandAttribute()
    drop_index        = CommandAttribute()
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
    find              = ReadAttribute()
    aggregate         = ReadAttribute()
    uuid_subtype      = motor.ReadWriteProperty()
    full_name         = motor.ReadOnlyProperty()

class EmbeddedDocument(BaseDocument):
    pass  

class Document(BaseDocument):
    meta = {}

    @classmethod
    def fields_dict(cls):
        fields = {}
        for name, attr in cls.__dict__.items():
            if isinstance(attr, Field):
                fields.update({name: attr})
        return fields

    @classmethod
    def get_database(cls):
        connection_name = (cls.meta['connection'] if 'connection' in cls.meta
                            else None)
        db_name = cls.meta['db'] if 'db' in cls.meta else None
        db = Connection.get_db(connection_name, db_name)
        return db

    @classmethod
    def get_collection(cls):
        db = cls.get_database()
        collection_name = (cls.meta['collection'] if 'collection' in cls.meta
                            else util.camel_to_underline(cls.__name__))
        collection = db[collection_name]
        return collection

      
