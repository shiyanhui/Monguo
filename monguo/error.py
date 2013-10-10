# -*- coding: utf-8 -*-

__all__ = ['ConnectionError', 'AssignmentError', 'RequiredError', 
            'UniqueError', 'CandidateError']

REQUIRED_MESSAGE = 'field %s required!'
UNIQUE_ERROR     = 'field %s is not unique!'
CANDIDATE_ERROR  = 'field %s not in candidate!'

class MonguoBaseError(Exception):
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return repr(self.message)

class ConnectionError(MonguoBaseError):
    pass

class AssignmentError(MonguoBaseError):
    pass

class FieldCheckError(MonguoBaseError):
    def __init__(self, base_message, field=None, **kwargs):
        super(FieldCheckError, self).__init__(**kwargs)

        if self.message is None:
            self.message = base_message % str('' if field is None else field)

class RequiredError(FieldCheckError):
    def __init__(self, field=None, **kwargs):
        super(RequiredError, self).__init__(REQUIRED_MESSAGE, 
                                                field=field, **kwargs)

class UniqueError(FieldCheckError):
    def __init__(self, field=None, **kwargs):
        super(RequiredError, self).__init__(UNIQUE_ERROR, 
                                                field=field, **kwargs)

class CandidateError(FieldCheckError):
    def __init__(self, field=None, **kwargs):
        super(RequiredError, self).__init__(CANDIDATE_ERROR, 
                                                field=field, **kwargs)



