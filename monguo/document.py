#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: lime
# @Date:   2013-10-25 19:45:09
# @Last Modified by:   Lime
# @Last Modified time: 2014-06-14 23:00:20

import sys
import inspect
import types
import motor
import util

from tornado import gen
from bson.dbref import DBRef
from bson.objectid import ObjectId
from connection import Connection
from error import *
from field import *
from connection import Connection
from validator import Validator


__all__ = ['BaseDocument', 'EmbeddedDocument', 'Document']


class MonguoOperation(object):
    '''
    The query operation. 

    Each one corresponds to the same name method of motor.
    '''
    def bound_method(self, monguo_method):
        '''
        Bound monguo method to motor method.

        :Parameters:
          - `monguo_method`: The method to be bounded.
        '''
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
    '''Meta class of Document.'''

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
                    new_attr = staticmethod(attr)
                    setattr(new_class, name, new_attr)
        
        return new_class


class BaseDocument(object):
    '''The document base, not support query operations.'''

    @classmethod
    def fields_dict(cls):
        '''Get all the Field instance attributes.'''

        fields = {}
        for name, attr in cls.__dict__.items():
            if isinstance(attr, Field):
                fields.update({name: attr})
        return fields

    @classmethod
    def validate_document(cls, document):
        '''Validate the given document.

        :Parameters:
          - `document`: The document to be validated.
        '''
        if not isinstance(document, dict):
            raise TypeError("Argument 'document' should be dict type.")

        _document = {}
        fields_dict = cls.fields_dict()

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
                    value = attr.document.validate_document(value)
                _document[name] = value

        return _document

   
class EmbeddedDocument(BaseDocument):
    '''The embedded document, not support query operations.'''
    pass  


class Document(BaseDocument):
    '''
    The ORM core, supports `all the query operations of motor 
    <http://motor.readthedocs.org/en/stable/api/motor_collection.html>`_.'''

    __metaclass__     = MonguoMeta
    meta              = {}
    
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
        '''Get the database name related to `cls`.'''

        db_name = (cls.meta['db'] if 'db' in cls.meta else 
            Connection.get_default_database_name())
        return db_name

    @classmethod
    def get_collection_name(cls):
        '''Get the collection name related to `cls`.'''

        collection_name = (cls.meta['collection'] if 'collection' in cls.meta
            else util.camel_to_underline(cls.__name__))
        return collection_name

    @classmethod
    def get_database(cls, pymongo=False):
        '''
        Get the database related to `cls`, it's an instance of 
        :class:`~motor.MotorDatabase`.

        :Parameters:
          - `pymongo`: Return pymongo.database if True.
        '''

        connection_name = cls.meta['connection'] if 'connection' in cls.meta else None
        db_name = cls.get_database_name()
        db = Connection.get_database(connection_name, db_name, pymongo)
        return db

    @classmethod
    def get_collection(cls, pymongo=False):
        '''
        Get the collection related to `cls`, it's an instance of 
        :class:`~motor.MotorCollection`.

        :Parameters:
          - `pymongo`: Return pymongo.collection if True.
        '''

        db= cls.get_database(pymongo)
        collection_name = cls.get_collection_name()
        collection = db[collection_name]
        return collection
    
    @classmethod
    @gen.coroutine
    def translate_dbref(cls, dbref):
        '''Get the document related with `dbref`.

        :Parameters:
          - `dbref`: The dbref to be translated.
        '''
        if not isinstance(dbref, DBRef):
            raise TypeError("'%s' isn't DBRef type.")

        if dbref.database is not None:
            connection_name = cls.meta['connection'] if 'connection' in cls.meta else None
            db = Connection.get_database(connection_name, dbref.database)
        else:
            db = cls.get_database()

        collection = db[dbref.collection]
        result = yield collection.find_one({'_id': ObjectId(dbref.id)})
        raise gen.Return(result)

    @classmethod
    @gen.coroutine
    def translate_dbref_in_document(cls, document, depth=1):
        '''Translate dbrefs in the specified `document`.

        :Parameters:
          - `document`: The specified document.
          - `depth`: The translate depth.
        '''
        if not isinstance(document, dict):
            raise TypeError("Argument 'document' should be dict type.")

        for name, value in document.items():
            if isinstance(value, DBRef):
                document[name] = yield cls.translate_dbref(value)
                if depth > 1:
                    document[name] = yield cls.translate_dbref_in_document(
                        document[name], depth - 1)

        raise gen.Return(document)

    @classmethod
    @gen.coroutine
    def translate_dbref_in_document_list(cls, document_list, depth=1):
        '''Translate dbrefs in the document list.

        :Parameters:
          - `document_list`: The specified document list.
          - `depth`: The translate depth.
        '''
        if not isinstance(document_list, (list, tuple)):
            raise TypeError("Argument document_list should be list or tuple tpye.")

        for document in document_list:
            document = yield cls.translate_dbref_in_document(document, depth)

        raise gen.Return(document_list)

    @classmethod
    @gen.coroutine
    def to_list(cls, cursor, length=None):
        '''Warp cursor.to_list() since `length` is required in `cursor.to_list`'''

        resut = []

        if length is not None:
            assert isinstance(length, int)
            reuslt = yield cursor.to_list(length=length)
        else:
            while (yield cursor.fetch_next):
                resut.append(cursor.next_object())

        raise gen.Return(resut)


    @classmethod
    def get_gridfs(cls, async=True):
        if async:
            db = Connection.get_database()
            fs = motor.MotorGridFS(db)
        else:
            db = Connection.get_database(pymongo=True)
            fs = gridfs.GridFS(db)

        return fs
