# -*- coding: utf-8 -*-

import re

def camel_to_underline(camel):
    if not isinstance(camel, basestring):
        raise TypeError('camel should be string type!')
        
    return ''.join([''.join(('_', item.lower())) 
        if item.isupper() and index else item.lower() 
        for index, item in enumerate(camel)])

def legal_variable_name(name):
    regex = re.compile('^[_a-zA-Z][_a-zA-Z0-9]*$')
    if regex.match(str(name)):
        return True
    return False
