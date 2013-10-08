# -*- coding: utf-8 -*-

def camel_to_underline(camel):
    if not isinstance(camel, basestring):
        raise TypeError('camel should be string type!')
        
    return ''.join([''.join(('_', item.lower())) 
        if item.isupper() and index else item.lower() 
        for index, item in enumerate(camel)])


