.. _index:

Welcome to PokeAlarm's documentation!
=====================================

.. image:: images/logo.png
    :align: center

|discord| |nbsp| |patron| |nbsp| |repo| |nbsp| |issues|

PokeAlarm is a highly configurable application that filters and relays alerts
about Pokemon Go to your favorite online service, allowing you to be first to
know of any rare spawns or raids.


.. toctree::
   :titlesonly:
   :maxdepth: 1
   :caption: Initial Setup
   :glob:

   getting-started/installation
   getting-started/faq

.. toctree::
   :titlesonly:
   :maxdepth: 1
   :caption: Basic Configuration

   configuration/server-settings
   configuration/events/index
   configuration/filters/index
   configuration/alarms/index


.. toctree::
   :titlesonly:
   :maxdepth: 1
   :caption: Advanced Configuration

   configuration/rules
   configuration/managers
   configuration/geofences


.. toctree::
   :titlesonly:
   :maxdepth: 1
   :caption: Guides
   :glob:

   Getting Started <guides/getting-started-guide>


.. toctree::
   :titlesonly:
   :maxdepth: 1
   :caption: Other
   :glob:

   Webhook Standards <miscellaneous/webhook-standard>
   Patch Notes <miscellaneous/patch-notes>
   Caching <miscellaneous/object-caching>
   Docker <miscellaneous/docker>
   Location Services <miscellaneous/location-services>
   Contributing <miscellaneous/contributing>


.. |discord| image:: https://discordapp.com/api/guilds/215181169761714177/widget.png?style=shield
    :target: https://discord.gg/S2BKC7p
.. |patron| image:: https://img.shields.io/badge/Donate-Patron-orange.svg
    :target: https://www.patreon.com/pokealarm
.. |repo| image:: https://img.shields.io/badge/github-PokeAlarm-green.svg
    :target: https://github.com/PokeAlarm/PokeAlarm
.. |issues| image:: https://img.shields.io/github/issues/PokeAlarm/PokeAlarm.svg
    :target: https://github.com/PokeAlarm/PokeAlarm/issues
.. |nbsp| unicode:: 0xA0
   :trim:
