#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: lime
# @Date:   2013-10-25 19:45:09
# @Last Modified by:   lime
# @Last Modified time: 2013-11-11 20:22:37

import re

def camel_to_underline(camel):
    if not isinstance(camel, str):
        raise TypeError('camel should be string type!')
        
    return ''.join([''.join(('_', item.lower())) 
           if item.isupper() and index else item.lower() 
           for index, item in enumerate(camel)])

def legal_variable_name(name):
    regex = re.compile('^[_a-zA-Z][_a-zA-Z0-9]*$')
    if regex.match(str(name)):
        return True
    return False

def isnum(value):
    try:
        float(value)
    except:
        return False
    else:
        return True
