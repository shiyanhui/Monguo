#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: lime
# @Date:   2013-11-07 14:45:40
# @Last Modified by:   lime
# @Last Modified time: 2014-03-26 15:24:22

try:
    from setuptools import setup, Feature
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, Feature

import monguo

classifiers = """\
Intended Audience :: Developers
License :: OSI Approved :: Apache Software License
Development Status :: 5 - Production/Stable
Natural Language :: English
Programming Language :: Python :: 2
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.0
Programming Language :: Python :: 3.3
Operating System :: MacOS :: MacOS X
Operating System :: Unix
Programming Language :: Python
Programming Language :: Python :: Implementation :: CPython
"""

version = monguo.__version__
description = 'Asynchronous MongoDB ORM for Tornado'
long_description = open("README.rst").read()
packages = ['monguo']

setup(name='monguo',
    version=version,
    packages=packages,
    description=description,
    long_description=long_description,
    author='Lime YH.Shi',
    author_email='shiyanhui66@gmail.com',
    url='https://github.com/shiyanhui/monguo',
    install_requires=[],
    license='http://www.apache.org/licenses/LICENSE-2.0',
    classifiers=filter(None, classifiers.split('\n')),
    keywords=[
        "monguo", "mongo", "mongodb", "pymongo", "gridfs", "bson", "motor", 
        "tornado", "ORM", "asynchronous"
    ],
    zip_safe=False,
)
