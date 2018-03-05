======
Monguo
======

.. image:: https://github.com/shiyanhui/monguo/blob/master/doc/source/_static/monguo.jpg?raw=true
	:width: 200px
	
:Info: Monguo is a full-featured, asynchronous MongoDB_ ORM with Motor_ dirver for Tornado_ applications.
:Author: Lime YH.Shi

.. image:: https://img.shields.io/pypi/v/monguo.svg
        :target: https://crate.io/packages/monguo

.. image:: https://img.shields.io/pypi/dm/monguo.svg
        :target: https://crate.io/packages/monguo

Installation
============
    
.. code-block:: bash

    $ pip install monguo

Dependencies
============

Monguo works in all the environments officially supported by Tornado_ and Motor_. It requires:

* Tornado_ >= 3.0
* Motor_ >= 0.2

Examples
========

.. code-block:: python
    
    from monguo import *

    Connection.connect('db') # connect to database

    class UserDocument(Document):
        name  = StringField(required=True, unique=True, max_length=20)
        email = EmailField(required=True)
        age   = IntegerField()
        sex   = StringField(default='male', candidate=['male', 'female'])

        meta = {
            'collection': 'user'
        }

        @gen.coroutine
        def get_user_list(skip=0, limit=None):
            cursor = UserDocument.find().skip(skip)

            if limit is not None:
                assert isinstance(limit, int) and limit > 0
                cursor.limit(limit)

            user_list = yield cursor.to_list(None)
            raise gen.Return(user_list)

    # insert
    user_id = yield UserDocument.insert({
        'name': 'Bob',
        'email': 'bob@gmail.com'
    })

    # query
    user = yield UserDocument.find_one({'name': 'Bob'})
    user_list = yield UserDocument.get_user_list()

    # update
    yield UserDocument.update(
        {'_id': user_id}, 
        {'$set': {'age': 19}})
    
    # delete
    yield UserDocument.remove({'_id': user_id})


.. _MongoDB: http://mongodb.org
.. _Tornado: http://tornadoweb.org
.. _Motor: https://github.com/mongodb/motor

