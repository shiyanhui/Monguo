# -*- coding: utf-8 -*-

import sys
import inspect
import motor
import types
import util

from tornado import gen
from bson.son import SON
from connection import Connection
from error import *
from field import Field, DictField
from connection import Connection
from validator import Validator


class MonguoOperation(object):
    def bound_method(self, monguo_method):
        @classmethod
        def method(cls, *args, **kwargs):
            collection = cls.get_collection()
            motor_method = getattr(collection, monguo_method)

            validator = Validator(cls, collection)
            try:
                validate_method = getattr(validator, monguo_method)
                args, kwargs = validate_method(*args, **kwargs)
            except AttributeError:
                pass
            return motor_method(*args, **kwargs)
        return method
    

class MonguoMeta(type):
    def __new__(cls, name, bases, attrs):
        new_class = type.__new__(cls, name, bases, attrs)

        for base in reversed(inspect.getmro(new_class)):
            for name, attr in base.__dict__.items():
                if isinstance(attr, Field):
                    if not util.legal_variable_name(name):
                        raise FieldNameError(field=name)

                elif isinstance(attr, MonguoOperation):
                    new_attr = attr.bound_method(name)
                    setattr(new_class, name, new_attr)

                elif isinstance(attr, types.FunctionType):
                    new_attr = staticmethod(gen.coroutine(attr))
                    setattr(new_class, name, new_attr)
        return new_class


class BaseDocument(object):
    @classmethod
    def fields_dict(cls):
        fields = {}
        for name, attr in cls.__dict__.items():
            if isinstance(attr, Field):
                fields.update({name: attr})
        return fields

    @classmethod
    def validate_document(cls, document_cls, document):
        if not issubclass(document_cls, BaseDocument):
            raise TypeError("Argument 'document_cls' should be Document type")

        if not isinstance(document, dict):
            raise TypeError("Argument 'document' should be dict type.")

        _document = {}
        fields_dict = document_cls.fields_dict()

        for name, attr in document.items():
            if not util.legal_variable_name(name):
                raise NameError("%s named error." % name)

            if name not in fields_dict:
                raise UndefinedFieldError(field=name)

        for name, attr in fields_dict.items():
            if (attr.required and not document.has_key(name) 
                              and attr.default is None):
                raise RequiredError(field=name)

            value = None
            if (attr.required and not document.has_key(name) 
                              and attr.default is not None):
                value = attr.default
            elif document.has_key(name):
                value = document[name]

            if value is not None:
                if not isinstance(attr, DictField):
                    value = attr.validate(value)
                else:
                    value = cls.validate_document(attr.document, value)
            _document[name] = value
        return _document

   
class EmbeddedDocument(BaseDocument):
    pass  


class Document(BaseDocument):
    __metaclass__      = MonguoMeta
    meta               = {}
    
    create_index      = MonguoOperation()
    drop_indexes      = MonguoOperation()
    drop_index        = MonguoOperation()
    drop              = MonguoOperation()
    ensure_index      = MonguoOperation()
    reindex           = MonguoOperation()
    rename            = MonguoOperation()
    find_and_modify   = MonguoOperation()
    map_reduce        = MonguoOperation()
    update            = MonguoOperation()
    insert            = MonguoOperation()
    remove            = MonguoOperation()
    save              = MonguoOperation()
    index_information = MonguoOperation()
    count             = MonguoOperation()
    options           = MonguoOperation()
    group             = MonguoOperation()
    distinct          = MonguoOperation()
    inline_map_reduce = MonguoOperation()
    find_one          = MonguoOperation()
    find              = MonguoOperation()
    aggregate         = MonguoOperation()
    uuid_subtype      = MonguoOperation()
    full_name         = MonguoOperation()

    @classmethod
    def get_database_name(cls):
        db_name = (cls.meta['db'] if 'db' in cls.meta else 
                   Connection.get_default_database_name())
        return db_name

    @classmethod
    def get_database(cls):
        connection_name = (cls.meta['connection'] if 'connection' in cls.meta
                           else None)
        db_name = cls.get_database_name()
        db = Connection.get_database(connection_name, db_name)
        return db

    @classmethod
    def get_collection_name(cls):
        collection_name = (cls.meta['collection'] if 'collection' in cls.meta
                           else util.camel_to_underline(cls.__name__))
        return collection_name

    @classmethod
    def get_collection(cls):
        db= cls.get_database()
        collection_name = cls.get_collection_name()
        collection = db[collection_name]
        return collection
    
    def translate_dbref(cls, dbref):
        if not isinstance(dbref, DBRef):
            raise TypeError("'%s' isn't DBRef type.")

        if dbref.database is not None:
            connection_name = (cls.meta['connection'] if 'connection' in 
                               cls.meta else None)
            db = Connection.get_database(connection_name, dbref.database)
        else:
            db = cls.get_database()

        collection = db[dbref.collection]
        result = yield collection.find_one({'_id': ObjectId(dbref.id)})
        raise gen.Return(result)

    def translate_dbref_in_document(cls, document):
        for name, value in document.items():
            if isinstance(value, DBRef):
                document[name] = yield cls.translate_dbref(value)
        raise gen.Return(document)

    def translate_dbref_in_document_list(cls, document_list):
        for document in document_list:
            document = yield cls.translate_dbref_in_document(document)
        raise gen.Return(document_list)
      
