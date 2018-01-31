datefinder - extract dates from text
====================================

.. image:: https://img.shields.io/travis/dcronkite/datefinder/master.svg
    :target: https://travis-ci.org/dcronkite/datefinder
    :alt: travis build status

.. image:: https://img.shields.io/pypi/dm/datefinder.svg
    :target: https://pypi.python.org/pypi/datefinder/
    :alt: pypi downloads per day

.. image:: https://img.shields.io/pypi/v/datefinder.svg
    :target: https://pypi.python.org/pypi/datefinder
    :alt: pypi version

.. image:: https://img.shields.io/gitter/room/nwjs/nw.js.svg
    :target: https://gitter.im/datefinder/Lobby
    :alt: gitter chat


A python module for locating dates inside text. Use this package to extract all sorts 
of date like strings from a document and turn them into datetime objects.

This module finds the likely datetime strings and then uses the  
`dateparser <https://github.com/scrapinghub/dateparser>`_ package to convert 
to the datetime object.


Installation
------------

.. code-block:: sh

    pip install pip install git+ssh://git@github.com/dcronkite/datefinder.git


How to Use
----------


.. automodule:: datefinder
   :members: find_dates


.. code-block:: python

    In [1]: string_with_dates = """
       ...: ...
       ...: entries are due by January 4th, 2017 at 8:00pm
       ...: ...
       ...: created 01/15/2005 by ACME Inc. and associates.
       ...: ...
       ...: """

    In [2]: import datefinder

    In [3]: matches = datefinder.find_dates(string_with_dates)

    In [4]: for match in matches:
       ...:     print match
       ...:
    2017-01-04 20:00:00
    2005-01-15 00:00:00
    

    In [5]: string_with_durations = """
       ...: ...
       ...: Total Duration: 3h5m18s
       ...: ...
       ...: He left 3 years ago...
       ...: ...
       ...: """

    In [6]: matches = datefinder.find_dates(string_with_durations)

    In [7]: for match in matches:
       ...:     print match
       ...:
    3:05:18
    -1096 days


Support
-------

You can talk to the developers of the original datefinder on `Gitter <https://gitter.im/datefinder/Lobby>`_ or just submit an issue for this fork on `Github <https://github.com/dcronkite/datefinder/issues/>`_. 

