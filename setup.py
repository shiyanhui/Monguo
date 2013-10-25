# Don't force people to install distribute unless we have to.
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
Development Status :: 4 - Beta
Natural Language :: English
Programming Language :: Python :: 2
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
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
    version='0.1.2',
    packages=packages,
    description=description,
    long_description=long_description,
    author='Lime. Shi Yanhui',
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
