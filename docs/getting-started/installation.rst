Installation
=====================================

This guide will walk you through installing a fresh copy of PokeAlarm.

.. contents:: Table of Contents
   :depth: 1
   :local:

Prerequisites
-------------------------------------

This guide assumes the following:

- Latest version of
  `Python 2.7 <https://www.python.org/download/releases/2.7/>`_ installed.
- `Git <https://git-scm.com/downloads>`_ installed.
- `Monocle <https://github.com/Hydro74000/Monocle>`_,
  `RocketMap <https://github.com/RocketMap/RocketMap>`_, or another supported
  scanner successfully installed.
- You are using a quality text editor like Notepad++, Nano, or Vi(m).

.. warning:: Do **NOT** use (or even open) any files with Notepad or TextEdit -
   they change the encoding on the file and prevent it from loading correctly.


Installing
-------------------------------------

1. **Clone a local copy of PokeAlarm** - Navigate a new folder to install
   PokeAlarm in (It is recommended you store it in a different folder than
   your scanner). In a terminal, run the command
   ``git clone https://github.com/PokeAlarm/PokeAlarm.git`` to create a
   local copy of the project. This create a folder called 'PokeAlarm' that
   will contain the application.

2. **Install the Requirements** - In a terminal, navigate into the root folder
   of your PA installation. Run ``pip install -r requirements.txt --upgrade``.
   This will install and update the modules that PokeAlarm needs to run.

3. **Configure PokeAlarm** - Next you need to configure PokeAlarm.

   - :doc:`../configuration/server-settings` let you configure things like host
     IP, port, language, and more.
   - :doc:`../configuration/filters/index` represent which Events trigger
     notifications. You will need to create a filters file before starting PA.
   - :doc:`../configuration/alarms/index` represent where and how
     notifications. You will need to create an alarms file before starting PA.


Running
-------------------------------------

1. **Start PokeAlarm** - In a terminal, use the command
   ``python start_pokealarm.py`` to start PokeAlarm and begin listening for
   information. If successful, you will see the following in the output:

   .. code:: none

       PokeAlarm is listening for webhooks on: http://127.0.0.1:4000

.. note:: PokeAlarm installs some dependencies on the fly. If you encounter
   errors when first running a new service, try running as root (with `sudo`) to
   ensure it can install the dependency.

2. **Setup Scanner Webhook** - Next, configure your scanner to send information
   to PA's address.

   - **For Monocle:**
     The webhook info only works in `Hydro's fork <https://github.com/Hydro74000/Monocle>`_.

   - **For RocketMap:**
     Configure the webhook types to send info as explained in
     `RocketMap wiki <https://rocketmap.readthedocs.io/en/develop/extras/webhooks.html>`_.

   Finally, start your scanner. If everything is set up correctly, PA will start
   logging information about what it is doing to the console.

Updating
-------------------------------------

.. warning:: Updating PokeAlarm can be complicated if you edit files you aren't
   supposed to. For this reason, we recommend not to edit any files ending in
   ``.py``.

1. Check the :doc:`../miscellaneous/patch-notes` for any big changes
   that might break your current configuration.
2. Open up a command line and change directory to the root folder of your
   install.
3. Run the command ``git pull && pip install -r requirements.txt`` to update to
   the latest version.

.. |br| raw:: html
