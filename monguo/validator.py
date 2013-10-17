# -*- coding: utf-8 -*-

import re
import util

from tornado import gen
from field import *
from error import *
from connection import Connection


class Validator(object):
    def __init__(self, document_cls, collection):
        self.document_cls = document_cls
        self.pymongo_db = Connection.get_database(pymongo=True)
        self.collection = self.pymongo_db[collection.name]

    def __check_value(self, field, name, value):
        value = field.validate(value)
        if (field.unique and not field.in_list 
                         and util.legal_variable_name(name)):
            count = self.collection.find({name: value}).count()
            if count:
                raise UniqueError(field=name)

        return value

    def insert(self, doc_or_docs, **kwargs):
        from document import BaseDocument

        if not isinstance(doc_or_docs, (dict, list, tuple)):
            raise TypeError("Argument 'doc_or_docs' should be dict or list "
                            "type.")

        if isinstance(doc_or_docs, dict):
            doc_or_docs = [doc_or_docs]

        for index, doc in enumerate(doc_or_docs):
            new_doc = BaseDocument.validate_document(self.document_cls, doc)
            doc_or_docs[index] = new_doc

            for name, attr in self.document_cls.fields_dict().items():
                if attr.unique and not attr.in_list:
                    result = self.collection.find_one({name: new_doc[name]})
                    if result:
                        raise UniqueError(field=name)

        args = [doc_or_docs]
        return args, kwargs

    def save(self, to_save, **kwargs):
        if not isinstance(to_save, dict):
            raise TypeError("Argument 'to_save' should be dict.")

        if to_save.has_key('_id'):
            _id = to_save['_id']
            del to_save['_id']
            to_save, _ = self.insert(to_save)
            to_save['_id'] = _id
        else:
            to_save, _ = self.insert(to_save)

        args = [to_save]
        return args, kwargs

    def update(self, spec, document, upsert=False, **kwargs):
        def check_key_in_operator_fields(key):
            '''Check whether the field name in '$set' is validated.'''

            name_list = key.split('.')
            name_error = NameError("%s is an illegal key!", key)
            for name in name_list:
                if not (util.legal_variable_name(name) or name.isdigit() or 
                        name == '$'):
                    raise name_error

            if name_list.count('$') > 1:
                raise name_error

            if not util.legal_variable_name(name_list[0]):
                raise name_error

            if (name_list.count('$') == 1 and 
                    name_list[name_list.index('$') - 1].isdigit()):
                raise name_error

            return name_list

        def pre_deal(operator, value):
            if operator == '$set': 
                value = [value]

            elif operator == '$addToSet':
                if isinstance(value, dict) and '$each' in value:
                    if len(value.items()) > 1:
                        raise SyntaxError("There cant't be other keys except "
                                          "'$each'.")

                    value = value['$each']
                    if not isinstance(value, (list, tuple)):
                        raise TypeError("Value of '$each' should be list or "
                                        "tuple type.")
                else:
                    value = [value]

            elif operator == '$inc':
                if not util.isnum(value):
                    raise ValueError("Value in '$inc' must be number.")
                value = [value]

            elif operator == '$pushAll':
                if not isinstance(value, (list, tuple)):
                    raise TypeError("Value in '$pushAll' should be list or "
                                    "tuple.")
            elif operator == '$push':
                if isinstance(value, dict) and '$each' in value:
                    if len(value.items()) > 1:
                        raise SyntaxError("There cant't be other keys except "
                                          "'$each'.")

                    value = value['$each']
                    if not isinstance(value, (list, tuple)):
                        raise TypeError("Value of '$each' should be list or "
                                        "tuple type.")
                else:
                    value = [value]

            elif operator == '$bit':
                if not isinstance(value, dict):
                    raise TypeError("The field value of '$bit' shoud be dict "
                                    "type.")

                if len(value.items()) != 1:
                    raise ValueError("Can't have other key except 'and' and "
                                     "'or' in '$bit'")

                key = value.keys()[0]
                if key != 'and' and key != 'or':
                    raise ValueError("Key in '$bit' should be 'and' or 'or'.")

                if not isinstance(value[key], (int, long)):
                    raise TypeError("Value in '$bit' should be int or long "
                                    "type.")

                value = [value[key]]
            return value

        def post_deal(operator, attr, name, value):
            if operator == '$addToSet':
                if not isinstance(attr, (ListField, GenericListField)):
                    raise TypeError("The field added to is not an instance of "
                                    "ListField or GenericListField.")

            elif operator == '$inc':
                if not isinstance(attr, (IntegerField, FloatField)):
                    raise TypeError("The field assigned to is not an instance "
                                    "of IntegerField or FloatField.")

            elif operator == '$pushAll':
                if not isinstance(attr, (ListField, GenericListField)):
                    raise TypeError("The field added to is not an instance of "
                                    "ListField or GenericListField.")

            elif operator == '$push':
                if not isinstance(attr, (ListField, GenericListField)):
                    raise TypeError("The field added to is not an instance of "
                                    " ListField or GenericListField.")

            elif operator == '$bit':
                if not isinstance(attr, IntegerField):
                    raise TypeError("The field bitwith to is not an instance "
                                    "of IntegerField.")

            elif operator == '$unset':
                if not isinstance(attr, (GenericDictField, DictField)):
                    raise TypeError("%s should be in GenericDictField or"
                                    "DictField." % name)

                if isinstance(attr, DictField):
                    fields_dict = attr.document.fields_dict()
                    if name in fields_dict and fields_dict[name].required:
                        raise FieldDeleteError(field=name)

        def deal_with_operator(operator):
            for name, value in document[operator].items():
                value = pre_deal(operator, value)

                original_name = name
                # Is the field name in self.son[operator] is right? 
                name_list = check_key_in_operator_fields(name)
                name_without_dollar = '.'.join([name for name in name_list 
                                               if name != '$'])

                fields_dict = self.document_cls.fields_dict()

                if name_list[0] not in fields_dict:
                    raise UndefinedFieldError(field=name_list[0])
                
                current_attr = fields_dict[name_list[0]]
                if operator == '$unset':
                    last_name = name_list.pop()
                    if not name_list:
                        fields_dict = self.document_cls.fields_dict()
                        if name in fields_dict and fields_dict[name].required:
                            raise FieldDeleteError(field=name)

                for index, name in enumerate(name_list):
                    if name == '$' or name.isdigit():
                        if index != len(name_list) - 1:
                            next_name = name_list[index + 1]

                            if next_name.isdigit():
                                if isinstance(current_attr, ListField):
                                    current_attr = current_attr.field
                                elif isinstance(current_attr, 
                                                GenericListField):
                                    break
                                else:
                                    raise TypeError("item in %s should be "
                                                    "GenericListField or "
                                                    "ListField type." %
                                                    name)
                            else:
                                if isinstance(current_attr.field, DictField):
                                    current_attr = current_attr.field
                                elif isinstance(current_attr.field, 
                                                GenericDictField):
                                    break
                                else:
                                    raise TypeError("item in %s should be "
                                                    "GenericDictField or "
                                                    "DictField type." % name)
                        else:
                            if operator == '$unset':
                                post_deal(operator, current_attr, last_name,
                                          value)
                            else:
                                post_deal(operator, current_attr, 
                                          name_without_dollar, value)

                                for item in value:
                                    result = self.__check_value(current_attr,
                                                        name_without_dollar,
                                                        item)
                                    document[operator][original_name] = result
                            
                    else:
                        if index != len(name_list) - 1:
                            next_name = name_list[index + 1]

                            if util.legal_variable_name(next_name):
                                if isinstance(current_attr, 
                                              DictField):
                                    current_attr = (current_attr.document.
                                                    fields_dict()[next_name])

                                elif isinstance(current_attr, 
                                                GenericDictField):
                                    break
                                else:
                                    raise TypeError("'%s' isn't DictField or "
                                                    "GenericDictField type." %
                                                    name)
                            else:
                                if isinstance(current_attr, ListField):
                                    current_attr = current_attr.field
                                elif isinstance(current_attr, 
                                                GenericListField):
                                    break
                                else:
                                    raise TypeError("%s isn't ListField or "
                                                    "GenericListField type." %
                                                    name)
                        else:
                            if operator == '$unset':
                                post_deal(operator, current_attr, last_name,
                                          value)
                            else:
                                post_deal(operator, current_attr, 
                                          name_without_dollar, value)

                                for item in value:
                                    result = self.__check_value(current_attr,
                                                        name_without_dollar,
                                                        item)
                                    document[operator][original_name] = result


        update_operators = ['$inc', '$name', '$setOnInsert', '$set', '$unset', 
                            '$addToSet', '$pop', '$pullAll', '$pull', '$sort',
                            '$pushAll', '$push', '$each', '$slice', '$bit' ,
                            '$isolated']

        if not isinstance(spec, dict):
            raise TypeError("Argument 'spec' should be dict type.")

        if not isinstance(document, dict):
            raise TypeError("Argument 'document' should be dict type.")

        if not isinstance(upsert, bool):
            raise TypeError("Argument 'upsert' should be bool type.")

        kwargs.update({'upsert': upsert})

        result = self.collection.find_one(spec)
        if not upsert or result:
            contain_operator = False
            for name in document:
                if name in update_operators:
                    contain_operator = True
                    break

            if not contain_operator:
                document, _ = self.insert(document)
                return document, kwargs

            if document.has_key('$rename'):
                for name in document['$rename']:
                    raise NotSupportError(field=name)

            new_operators = ['$set', '$inc', '$addToSet', '$pushAll', '$push', 
                             '$bit', '$unset']

            for operator in new_operators:
                if document.has_key(operator):
                    deal_with_operator(operator)
        else:
            if document.has_key('$setOnInsert'):

                mongodb_version = (self.pymongo_db.command('buildInfo')
                                   ['version'])

                if mongodb_version < '2.4':
                    raise KeyError("Your Mongdb's version is %s, only version "
                                   "2.4+ support '$setOnInsert'." %
                                   mongodb_version)

                document = document['$setOnInsert']
                document, _ = self.insert(document)

        args = [spec, document]
        return args, kwargs
