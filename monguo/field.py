#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: lime
# @Date:   2013-10-25 19:45:09
# @Last Modified by:   lime
# @Last Modified time: 2013-11-27 15:30:18

import re
import util
import inspect
import sys
import os
import imp
import cPickle as pickle

from datetime import datetime, date, time
from bson.dbref import DBRef
from bson.binary import Binary
from bson.objectid import ObjectId
from error import *

__all__ = ['Field', 'StringField', 'IntegerField', 'BooleanField',
           'FloatField', 'EmbeddedDocumentField', 'GenericDictField', 
           'DictField', 'GenericListField', 'ListField', 'EmailField',
           'ReferenceField', 'ObjectIdField', 'DateTimeField', 'DateField',
           'TimeField', 'BinaryField']

class Field(object):
    '''Base field class.'''

    def __init__(self, required=False, default=None, unique=False, 
                 candidate=None, strict=False):
        '''
        :Parameters:
            - `required(optional)`: If the field is required. Whether it has to have a value or not. Defaults to False.
            - `default(optional)`: The default value for this field if no value has been set (or if the value has been unset).
            - `unique(optional)`: Is the field value unique or not. Defaultsto False.
            - `candidate(optional)`: The value to be chose from.
            - `strict(optional)`: Whether it is strict when validate the type. If true, the value only can be the specified type. For example, when assign to IntegerField, it can only be int or long type.
        '''
        self.required = required
        self.default = default
        self.unique = unique
        self.candidate = candidate
        self.strict = strict

        self._in_list = False

        if self.default is not None:
            self.default = self.check_type(self.default)

        if self.candidate is not None:
            if not isinstance(self.candidate, (list, tuple)):
                raise TypeError("'candidate' should be list or tuple type.")

            for index, item in enumerate(self.candidate[::]):
                self.candidate[index] = self.check_type(item)

            if self.default is not None and self.default not in self.candidate:
                raise ValueError("default value '%s' isn't in candidate %s" % 
                                 (self.default, self.candidate))

    @property
    def in_list(self):
        '''Whether the field is in a GenericListField or ListField.'''

        return self._in_list

    @in_list.setter
    def in_list(self, value):
        '''Set `in_list`.'''

        self._in_list = value

    def check_type(self, value):
        '''Validate the type of the value.'''

        return value

    def validate(self, value):
        '''Validate the value.'''

        value = self.check_type(value)

        if self.candidate and value not in self.candidate:
            raise ValidateError("'%s' not in '%s'." % (value, self.candidate))
        return value


class StringField(Field):
    '''A unicode string field.'''

    def __init__(self, regex=None, min_length=None, max_length=None, **kwargs):
        super(StringField, self).__init__(**kwargs)
        '''
        :Parameters:
            - `regex(optional)`: The regex to to be matched.
            - `min_length(optional)`: The min length of the string.
            - `max_length(optional)`: The max length of the string. 
        '''

        if regex is not None and not isinstance(regex, basestring):
            raise TypeError("Argument 'regex' should be string value.")

        if min_length is not None and not isinstance(min_length, (int, long)):
            raise TypeError("Argument 'min_length' should be integer value.")

        if max_length is not None and not isinstance(max_length, (int, long)):
            raise TypeError("Argument 'max_length' should be integer value.")

        self.regex = regex
        self.min_length = min_length
        self.max_length = max_length

    def check_type(self, value):
        if self.strict and not isinstance(value, basestring):
            raise TypeError("'%s' is not string type." % value)
        try:
            value = str(value)
        except:
            raise ValidateError("Can't convert '%r' to string." % value)
        return value

    def validate(self, value):
        value = super(StringField, self).validate(value)

        if self.min_length is not None and len(value) < self.min_length:
            raise ValidateError("String value is too short.")

        if self.max_length is not None and len(value) > self.max_length: 
            raise ValidateError("String value is too long.")

        if self.regex is not None and re.match(regex, value) is None:
            raise ValidateError("regex doesn't match.")

        return value


class IntegerField(Field):
    '''A int or long field.'''

    def __init__(self, min_value=None, max_value=None, **kwargs):
        super(IntegerField, self).__init__(**kwargs)
        '''
        :Parameters:
            - `min_value(optional)`: The min value of the field.
            - `max_value(optional)`: The max value of the field.
        '''
        if (min_value is not None and 
                         not isinstance(min_value, (int, long, float))):
            raise TypeError("Argument 'min_value' should be integer value.")

        if max_value is not None and not isinstance(max_value, (int, long)):
            raise TypeError("Argument 'max_value' should be integer value.")

        self.min_value = min_value
        self.max_value = max_value

    def check_type(self, value):
        if self.strict and not isinstance(value, (int, long)):
            raise TypeError("'%s' is not int or long type." % value)
        try:
            value = long(value)
        except Exception, e:
            raise ValidateError("'%s' cann't be converted to int value." %
                                value)
        return value

    def validate(self, value):
        value = super(IntegerField, self).validate(value)

        if self.min_value is not None and value < self.min_value:
            raise ValidateError("'%s' is smaller than %s." % 
                                (value, self.min_value))

        if self.max_value is not None and value > self.max_value:
            raise ValidateError("'%s' is larger than %s." % 
                                (self.value, self.max_value ))
        return value


class FloatField(Field):
    '''A float field.'''

    def __init__(self, min_value=None, max_value=None, **kwargs):
        '''
        :Parameters:
            - `min_value(optional)`: The min value of the field.
            - `max_value(optional)`: The max value of the field.
        '''
        super(FloatField, self).__init__(**kwargs)
        if (min_value is not None and 
                         not isinstance(min_value, (int, long, float))):
            raise TypeError("Argument 'min_value' should be number.")

        if max_value is not None and not isinstance(max_value, (int, long)):
            raise TypeError("Argument 'max_value' should be integer value.")

        self.min_value = min_value
        self.max_value = max_value

    def check_type(self, value):
        if self.strict and not isinstance(value, float):
            raise TypeError("'%s' is not float type." % value)
        try:
            value = long(value)
        except Exception, e:
            raise ValidateError("'%s' cann't be converted to int value." % 
                                value)
        return value

    def validate(self, value):
        value = super(FloatField, self).validate(value)

        if self.min_value is not None and value < self.min_value:
            raise ValidateError("'%s' is smaller than '%s'." % 
                                (value, self.min_value))

        if self.max_value is not None and value > self.max_value:
            raise ValidateError("'%s' is larger than '%s'." % 
                                (self.value, self.max_value ))
        return value


class BooleanField(Field):
    '''A bool field.'''

    def check_type(self, value):
        if self.strict and not isinstance(value, bool):
            raise TypeError("'%s' isn't bool type." % value)
        try:
            value = bool(value)
        except:
            raise ValidateError("Cann't convert '%s' to bool." % value)
        return  value

    def validate(self, value):
        value = super(BooleanField, self).validate(value)
        return value

class EmailField(StringField):
    '''Email field.'''

    EMAIL_REGEX = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'
        r")@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$)"
        r'|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$', re.IGNORECASE )

    def validate(self, value):
        value = super(EmailField, self).validate(value)
        if not EmailField.EMAIL_REGEX.match(value):
            raise ValidateError("'%s' is not email format." % value)
        return value

class GenericDictField(Field):
    '''Generic dict field. You can pust any data in it and it wouldn't be validated.'''

    def check_type(self, value):
        if self.strict and not isinstance(value, dict):
            raise TypeError("'%s' isn't dict type.")
        try:
            value = dict(value)
        except:
            raise ValidateError("Can't convert '%s' to dict." % value)
        return value

    def validate(self, value):
        value = super(GenericDictField, self).validate(value)
        return value

class DictField(GenericDictField):
    '''A dict field. The field in it will be validated.'''

    def __init__(self, document, **kwargs):
        '''
        :Parameters:
            - `document`: The embedded document class.
        '''
        from document import EmbeddedDocument
        if not issubclass(document, EmbeddedDocument):
            raise TypeError("Argument 'embedded_doc' should be "
                            "EmbeddedDocument type.")

        self.document = document
        super(DictField, self).__init__(**kwargs)

    def validate(self, value):
        value = super(DictField, self).validate(value)
        value = self.document.validate_document(value)

        for name, attr in self.document.fields_dict().items():
            if attr.unique and not attr.in_list:
                count = self.collection.find({name: value[name]}).count()
                if count:
                    raise UniqueError(field=name)

        return value

EmbeddedDocumentField = DictField

class GenericListField(Field):
    '''Generic list field. You can pust any data in it and it wouldn't be
       validated.
    '''

    def check_type(self, value):
        if self.strict and not isinstance(value, (list, tuple)):
            raise TypeError("'%s' isn't list or tuple typr.")
        try:
            value = list(value)            
        except:
            raise ValidateError("Can't convert '%s' to list" % value)
        return value

    def validate(self, value):
        value = super(GenericListField, self).validate(value)
        return value


class ListField(GenericListField):
    '''A list field. It can only hold one type of field in it.'''

    def __init__(self, field, **kwargs):
        if not isinstance(field, Field):
            raise ValueError("Argument field of ListField should be Field"
                             "type.")
        self.field = field
        self.field.in_list = True
        super(ListField, self).__init__(**kwargs)
    
    def validate(self, value): 
        value = super(ListField, self).validate(value)
        for index, item in enumerate(value[::]):
            value[index] = self.field.validate(item)
        return value


class ReferenceField(Field):
    '''The reference field.'''

    def __init__(self, reference=None, **kwargs):
        '''
        :Parameters:
            - `reference`: The document class referenced to.
        '''

        self.reference = reference
        super(ReferenceField, self).__init__(**kwargs)

    def get_reference(self, reference):
        from document import Document

        if reference is None:
            return reference

        result = None
        if isinstance(reference, basestring):
            stack = inspect.stack()
            for _ in stack:
                if _[1] is not None:
                    name = inspect.getmodulename(_[1])
                    _ = imp.find_module(name, [os.path.dirname(_[1])])
                    fp, _ = _[0], _[1:] 
                    try:
                        module = imp.load_module(name, fp, *_)
                        result = getattr(module, reference)
                        break
                    except:
                        pass
                    finally:
                        if fp:
                            fp.close()
                    
        elif issubclass(reference, Document):
            result = reference

        if result is None:
            raise Exception("Couldn't find %s" % reference)

        return result

    def check_type(self, value):
        if not isinstance(value, DBRef):
            raise TypeError("Value '%s' isn't DBRef type." % value)
        return value

    def validate(self, value):
        self.reference = self.get_reference(self.reference)

        value = super(ReferenceField, self).validate(value)

        if self.reference is not None:
            if (value.database is not None and 
                    self.reference.get_database_name() != value.database):
                raise ValidateError("Database is different betwwen '%s' and "
                                    "'%s'" % (self.reference.get_database_name(
                                    ), value.database))

            if value.collection != self.reference.get_collection_name():
                raise ValidateError("Collection is different betwwen '%s' and "
                                    "'%s'" % (self.reference.
                                    get_collection_name, value.collection))
        return value


class ObjectIdField(Field):
    '''An ObjectId field.'''

    def check_type(self, value):
        if self.strict and not isinstance(value, ObjectId):
            raise TypeError("Value '%s' isn't ObjectId type." % value)
        try:
            value = ObjectId(value)
        except:
            raise ValidateError("Cann't convert '%s' to ObjectId." % value)

        return value

    def validate(self, value): 
        value = super(ObjectId, self).validate(value)
        return value

class DateTimeField(Field):
    '''An `datetime.datetime` field.'''

    def check_type(self, value):
        if not isinstance(value, datetime):
            raise TypeError("Value '%s' should be datetime.datetime." 
                            % value)
        return value

    def validate(self, value):
        value = super(DateTimeField, self).validate(value)
        return value

class DateField(Field):
    '''An `datetime.date` field'''

    def check_type(self, value):
        if not isinstance(value, date):
            raise TypeError("Value '%s' isn't datetime.date type" % value)

        return value

    def validate(self, value):
        value = super(DateField, self).validate(value)
        return value

class TimeField(Field):
    '''An `datetime.time` field'''

    def check_type(self, value):
        if not isinstance(value, time):
            raise TypeError("Value '%s' isn't datetime.time type" % value)

        return value

    def validate(self, value):
        value = super(TimeField, self).validate(value)
        return value

class BinaryField(Field):
    '''Binary Field'''

    def check_type(self, value):
        if self.strict and not isinstance(value, Binary):
            raise TypeError("Value '%s' isn't Binary type." % value)

        if not isinstance(value, Binary):
            try:
                value = Binary(value)
            except:
                raise ValidateError("Cann't convert '%s' to Binary." % value)

        return value

    def validate(self, value):
        value = super(BinaryField, self).validate(value)
        return value