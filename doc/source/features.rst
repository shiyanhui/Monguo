==============
Monguo Features
==============

Since Monguo wraps Motor_, it has all the features Motor_ has. But relative to other ORMs, it has features bellow.

Non-Blocking
============
Monguo is an asynchronous MongoDB ORM with driver Motor_ which never blocks Tornado's IOLoop while connecting to MongoDB or performing I/O.

Featureful
==========
Monguo wraps all of Motor's query API. You can query database easily.

Lightweight
===========
Monguo provides basic API, you can wrap it to higher API in you custom document class.

.. _Tornado: http://tornadoweb.org/
.. _Motor: https://github.com/mongodb/motor
