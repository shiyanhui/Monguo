.. Contents::

Overview
========

Monguo is an asynchronous MongoDB_ ORM with Motor_ dirver for Tornado_ applications.

.. image:: _static/monguo.jpg

.. image:: https://pypip.in/v/monguo/badge.png
        :target: https://crate.io/packages/monguo

.. image:: https://pypip.in/d/monguo/badge.png
        :target: https://crate.io/packages/monguo

Installation
============
    
.. code-block:: bash

    $ pip install monguo

Dependencies
============

* Tornado_ >= 3.0
* Motor_ >= 0.2

Quick Start
===========

Creating a connection
---------------------

Just call :meth:`Connection.connect()` to create a connection. If you don't set `connection_name`, it will create a connection named `default`. If 
connection with the same name has been created, it will disconnect and remove 
it and push this connection to the top of connections stack, otherwise it 
push this connection to the top of connections stack directly. It will set 
this connection as the default connection.

.. code-block:: python
    
    from monguo.connection import Connection
    Connection.connect('db')

If you want to use replica set client, just set `replica_set=True`.

.. code-block:: python
    
    Connection.connect('db', replica_set=True)

You can also just create a connection only and set database later.

.. code-block:: python

    Connection.connect()
    Connection.switch_database('db')

Defining documents
------------------

Just inherit :class:`~monguo.document.Document` or 
:class:`~monguo.document.EmbeddedDocument` to create your document. Take a 
simple Tumblelog application for example. 

First import kinds of fields, :class:`~monguo.document.Document` and 
:class:`~monguo.document.EmbeddedDocument`.

.. code-block:: python
    
    from monguo.field import *
    from monguo.document import Document, EmbeddedDocument

Then define our documents.

UserDocument
````````````
We assume `UserDocument` has `name`, `email` and `age` fields. In `meta` we can
define the collection's name.

.. code-block:: python

    class UserDocument(Document):
        name  = StringField(required=True, unique=True, max_length=20)
        email = EmailField(required=True)
        age   = IntegerField()
        sex   = StringField(
            required=True, default='male', candidate=['male', 'female'])

        meta = {
            'collection': 'user'
        }
    
PostDocument
````````````
A post point to an author, we can use :class:`~monguo.field.ReferenceField` to 
define it. And we set comments as it's embedded document.

.. code-block:: python
    
    class PostDocument(Document):
        author       = ReferenceField(UserDocument, required=True)
        publish_time = DateTimeField(required=True)
        title        = StringField(required=True, max_length=100)
        contents     = StringField(max_length=5000)
        comments     = ListField(EmbeddedDocumentField(CommentDocument))

        meta = {
            'collection': 'post'
        }

CommentDocument
```````````````
The `CommentDocument` will be embedded in `PostDocument`.

.. code-block:: python

    class CommentDocument(EmbeddedDocument):
        commentor = ReferenceField(UserDocument, required=True)
        contents  = StringField(required=True, max_length=200)

Insert
------

We insert two users `Bob` and `Alice`. `Bob` publishs a post, and `Alice` 
comments it.

.. code-block:: python
    
    bob_id = yield UserDocument.insert({
        'name': 'Bob',
        'email': 'bob@gmail.com',
        'age': 19
    })

    alice_id = yield UserDocument.insert({
        'name': 'Alice',
        'email': 'alice@gmail.com',
        'sex': 'female',
        'age': 18
    })

We don't have to set bob's `sex` field since it's default value is 'male', it will be set automatically.

`Bob` publish a post.

.. code-block:: python

    from bson.dbref import DBRef
    from datetime import datetime

    post_id = yield PostDocument.insert({
        'author': DBRef(UserDocument.meta['collection'], bob_id),
        'publish_time': datetime.now(),
        'title': 'title',
    })


Update
------

`Alice` comments `Bob's` post.

.. code-block:: python

    comment = {
        'commentor': DBRef(UserDocument.meta['collection'], alice_id),
        'contents': 'I am comments.'
    }

    yield PostDocument.update(
        {'_id': post_id}, 
        {'$push': {'comments': comment}})

Query
-----

`Monguo` supports all `Motor's` query methods.

.. code-block:: python

    user = yield UserDocument.find_one({'name': 'Bob'})
    posts = yield PostDocument.find().to_list(None)

You can regard `Document` and your defined documents as 
`motor.MotorCollection`. It's equal to:

.. code-block:: python
    
    collection = UserDocument.get_collection()    
    user = yield collection.find_one({'name': 'Bob'})

    collection = PostDocument.get_collection()
    posts = yield collection.find().to_list(None)

Delete
-------

We can delete Bob from `user` collection.

.. code-block:: python
    
    collection = yield UserDocument.remove({'name': 'Bob'})

Defining higher API
-------------------

You can define higher API in your document, take `UserDocoment` for example.

.. code-block:: python

    from tornado import gen

    class UserDocument(Document):
        name  = StringField(required=True, unique=True, max_length=20)
        email = EmailField(required=True)
        age   = IntegerField()
        sex   = StringField(
            required=True, default='male', candidate=['male', 'female'])

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

It's simple to call it.

.. code-block:: python

    user_list = yield UserDocument.get_user_list()

You can get more in API dcouemnt.

API
============

.. toctree::

   api/index

More
============

Monguo has the same `CURD API` as Motor_, you can read `Motor's document <http://motor.readthedocs.org/>`_.

.. _MongoDB: http://mongodb.org
.. _Tornado: http://tornadoweb.org
.. _Motor: https://github.com/mongodb/motor