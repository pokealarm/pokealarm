.. _object-caching:

Object Caching
=====================================

.. contents:: Table of Contents
   :depth: 2
   :local:

Prerequisites
-------------------------------------

This guide assumes:

1. You have a functional PokeAlarm installation
2. You have a basic understanding of how to manage binary files
3. You have read and understood the available Command Line Arguments in
   the :doc:`../configuration/server-settings` wiki

Introduction
-------------------------------------

PokeAlarm uses `Cache` objects to store information that is not present on
runtime. The cached objects store information such as ``gym-info`` and other
dynamic objects sent into PokeAlarm via webhook. Cached data is used for
internal calculations as well as to provide details for :doc:`../configuration/events/index`
in :doc:`../configuration/alarms/index`.

Caching Methods
-------------------------------------

There are currently two methods available for object caching:

+--------------------+------------------------------------------------------------------+
| Caching Method     | Description                                                      |
+--------------------+------------------------------------------------------------------+
| `mem`              | Caches data to memory only, information is lost between sessions |
+--------------------+------------------------------------------------------------------+
| `file`             | Caches data to binary files located in the `cache` folder        |
+--------------------+------------------------------------------------------------------+

.. note:: If no cache-type is selected, ``mem`` will be chosen as the default.

Memory Cache
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When using the ``mem`` cache type, cached data is stored in memory only and is
cleared whenever PA exits.  This will cause all :doc:`../configuration/events/index`
fields which require this data to display an ``unknown`` or ``null`` value until
the data is received by PA through webhooks.

Binary File Cache
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When using the ``file`` cache type, cached data is written to a binary file
located in the ``cache/`` directory. Each :doc:`../configuration/managers` has
a unique binary cache file stored as ``cache/<manager_name>.cache``. Cached
data is backed up to this binary file once per minute and immediately before
PA exits.

Multiple Instances
-------------------------------------

Using File caching with multiple instances can cause conflicts as cache files
are stored under ``<manager_name>.cache``. When using the ``file`` cache type
and multiple instances, take caution and ensure that all managers are assigned
an explicitly unique name.

Clearing Cache
-------------------------------------

+ **Memory Cache** is cleared whenever PA exits for any reason.
+ **File Caches** may be cleared by deleting the ``cache/<manager_name>.cache``
  file that corresponds to the manager you wish to clear the cache for. (To
  clear all cached data, delete all files in the cache folder). PA will need
  to be restarted once cache files are erased.
