# -*- coding: utf-8 -*-

__all__ = ['ConnectionError', 'AssignmentError', 'RequiredError']

class MonguoBaseError(Exception):
    REQUIRED_MESSAGE = 'field %s required!'

class ConnectionError(MonguoBaseError):
    pass

class AssignmentError(MonguoBaseError):
    pass

class RequiredError(MonguoBaseError):
    def __init__(self, message=None, field=None):
        self.message = (MonguoBaseError.REQUIRED_MESSAGE 
                            if message is None else message)
        if message is not None:
            self.message = message
        elif field_name is not None:
            self.message = MonguoBaseError.REQUIRED_MESSAGE % str(field_name)
        else:
            self.message = MonguoBaseError.REQUIRED_MESSAGE % ''

    def __str__(self):
        return repr(self.message)







