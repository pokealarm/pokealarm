Events
=======

.. contents:: Table of Contents
   :depth: 1
   :local:

Prerequisites
-------------------------------------

This guide assumes the following:

+ You are using the latest version of PokeAlarm.


Introduction
-------------------------------------

In PokeAlarm, an **Event** represents something of interest that has happened in
the World. Events can be several different things - a new monster spawning, a
gym changing teams, or a new raid appearing. There are 5 different categories
for Events, each with different information:

.. toctree::
   :maxdepth: 1

   monster-events
   Stop-DTS
   Gym-DTS
   Egg-DTS
   Stop-DTS

.. _events_dts
Dynamic Text Substitutions
-------------------------------------

Dynamic Text Substitutions (or DTS) are special text that can be used to
customize notifications based on the triggered Event. These values are
surrounded with diamond brackets (`<` and `>`) and will by substituted with a
value based on the Event in question. For example, a notification with the
following text:

.. code-block:: none

     A wild <mon_name> has appeared! It has <iv>% IVs!

Could be substituted to the following:

.. code-block:: none

    A wild Charmander has appeared! It has 100.0% IVs!

Or, it could appear like this:

.. code-block:: none

     A wild Pidgey has appeared! It has 55.6% IVs!

The DTS that you can use vary by type of Event - make sure to check the page for
each type to which DTS can be used.


Missing Information
-------------------------------------

.. note:: You can accept or reject an event based on the state of missing
          information. See the ``is_missing_info`` restriction on the
          :doc:`../filters/index` page for instructions.

When PA doesn't have the correct information needed to correctly do a
subsitution, it may replace it with one of the following:

+ ?
+ ???
+ unknown

This can happen for a variety of reasons - but generally is because the scanner
did not send the information needed in the webhook. PA does it's best to fill in
the gaps by sharing and caching information between seperate webhooks (like gym
names or teams), but some info may require a settings update with your scanner
(like IVs or CP).
