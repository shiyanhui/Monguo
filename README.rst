======
Monguo
======

.. image:: https://github.com/shiyanhui/monguo/blob/master/doc/source/_static/monguo.jpg?raw=true
	:width: 200px
	
:Info: Monguo is a full-featured, asynchronous MongoDB_ ORM with Motor_ dirver for Tornado_ applications.
:Author: Lime YH.Shi

.. image:: https://pypip.in/v/monguo/badge.png
        :target: https://crate.io/packages/monguo

.. image:: https://pypip.in/d/monguo/badge.png
        :target: https://crate.io/packages/monguo

.. _MongoDB: http://mongodb.org/
.. _Motor: https://github.com/mongodb/motor/
.. _Tornado: http://tornadoweb.org/


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

    class UserDocument(Document):
        name  = StringField(required=True, unique=True, max_length=20)
        email = EmailField(required=True)
        age   = IntegerField()
        sex   = StringField(required=True, default='male', candidate=['male', 'female'])

        meta = {
            'collection': 'user'
        }

        @gen.coroutine
        def get_user_list(skip=10, limit=5):
            user_list = yield UserDocument.find().to_list(limit)
            raise gen.Return(user_list)


    Connection.connect('db') # connect to database

    # insert
    user_id = yield UserDocument.insert({
        'name': 'Bob',
        'email': 'bob@gmail.com'
    })

    # update
    yield UserDocument.update(
        {'_id': user_id}, 
        {'$set': {'age': 19}})

    # query
    user = yield UserDocument.find_one({'name': 'Bob'})
    user_list = yield UserDocument.get_user_list()


.. _MongoDB: http://mongodb.org/
.. _Tornado: http://tornadoweb.org/
.. _Motor: https://github.com/mongodb/motor/

