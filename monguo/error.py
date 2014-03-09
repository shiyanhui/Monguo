#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: lime
# @Date:   2013-10-25 19:45:09
# @Last Modified by:   lime
# @Last Modified time: 2014-03-09 15:16:46

__all__ = ['ConnectionError', 'AssignmentError', 'RequiredError', 
           'UniqueError', 'CandidateError', 'UndefinedFieldError',
           'FieldDeleteError', 'FieldRenameError', 'FieldNameError', 
           'NotSupportError', 'FieldValueError', 'ValidateError']

ASSIGNMENT_ERROR   = "Variable '%s' cant't be assgined!"
REQUIRED_MESSAGE   = "Field '%s' required!"
UNIQUE_ERROR       = "Field '%s' is unique!"
CANDIDATE_ERROR    = "Field '%s' not in candidate!"
UNDEFINED_ERROR    = "Undefined field '%s' in document!"
FIELD_DELETE_ERROR = "Field '%s' is required, you can't delete it!"
FIELD_RENAME_ERROR = "Field '%s' can't be renamed!"
FIELD_NAME_ERROR   = "Field name '%s' can't contain character '.' or '$'!"
NOT_SUPPORT_ERROR  = "Operation %s is not supported."
FIELD_VALUE_ERROR  = "Value '%s' is not %s."


class MonguoBaseError(Exception):
    '''Base Monguo error class.'''
    
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return repr(self.message)


class ConnectionError(MonguoBaseError):
    pass


class ValidateError(MonguoBaseError):
    pass


class NotSupportError(MonguoBaseError):
    def __init__(self, operation):
        self.operation = operation
    
    def __str__(self):
        return repr(NOT_SUPPORT_ERROR % self.operation)


class FieldValueError(MonguoBaseError):
    def __init__(self, value, field):
        self.value = value
        self.field = field
    
    def __str__(self):
        return repr(FIELD_VALUE_ERROR % (self.value, self.field))


class FieldCheckError(MonguoBaseError):
    def __init__(self, base_message, field=None, **kwargs):
        super(FieldCheckError, self).__init__(**kwargs)

        if self.message is None:
            self.message = base_message % str('' if field is None else field)


class AssignmentError(FieldCheckError):
    def __init__(self, field=None, **kwargs):
        super(AssignmentError, self).__init__(
            ASSIGNMENT_ERROR, field=field, **kwargs)


class RequiredError(FieldCheckError):
    def __init__(self, field=None, **kwargs):
        super(RequiredError, self).__init__(
            REQUIRED_MESSAGE, field=field, **kwargs)


class UniqueError(FieldCheckError):
    def __init__(self, field=None, **kwargs):
        super(UniqueError, self).__init__(
            UNIQUE_ERROR, field=field, **kwargs)


class CandidateError(FieldCheckError):
    def __init__(self, field=None, **kwargs):
        super(CandidateError, self).__init__(
            CANDIDATE_ERROR, field=field, **kwargs)


class UndefinedFieldError(FieldCheckError):
    def __init__(self, field=None, **kwargs):
        super(UndefinedFieldError, self).__init__(
            UNDEFINED_ERROR, field=field, **kwargs)


class FieldDeleteError(FieldCheckError):
    def __init__(self, field=None, **kwargs):
        super(FieldDeleteError, self).__init__(
            FIELD_DELETE_ERROR, field=field, **kwargs)


class FieldRenameError(FieldCheckError):
    def __init__(self, field=None, **kwargs):
        super(FieldRenameError, self).__init__(
            FIELD_RENAME_ERROR, field=field, **kwargs)


class FieldNameError(FieldCheckError):
    def __init__(self, field=None, **kwargs):
        super(FieldNameError, self).__init__(
            FIELD_NAME_ERROR, field=field, **kwargs)
