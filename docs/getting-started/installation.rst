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
  `Python 3.7+ <https://www.python.org/downloads/release/python-379/>`_ installed.
- `Git <https://git-scm.com/downloads>`_ installed.
- `Map'A'Droid <https://github.com/Map-A-Droid/MAD>`_,
  `RealDeviceMap <https://github.com/RealDeviceMap/RealDeviceMap>`_, or another supported
  scanner successfully installed.
- You are using a quality text editor like Notepad++, Nano, Vi(m) or VSCode.

.. warning:: Do **NOT** use (or even open) any files with Notepad or TextEdit -
   they change the encoding on the file and prevent it from loading correctly.


Installing
-------------------------------------

1. **Prepare your environment** - By installing a new Python project, it is
   strongly recommended to create an isolated environment to avoid package
   conflicts with other Python projects like MAD or RocketMAD. To do so,
   install ``sudo apt install python3-virtualenv`` if you still don't have it.
   Then create a new environment for PokeAlarm with
   ``virtualenv -p python3 ~/pokealarm_env`` and enter to it by
   typing ``source ~/pokealarm_env/bin/activate``. You must be in this PA env
   before running any commands starting by ``pip3`` or ``python3``.

2. **Clone a local copy of PokeAlarm** - Create a new folder to install
   PokeAlarm in. Do not install it in your scanner directory. In a terminal, 
   run the command ``git clone https://github.com/PokeAlarm/PokeAlarm.git``
   to create a local copy of the project. This will create a folder called
   'PokeAlarm' that will contain the application.

3. **Install the requirements** - In a terminal, navigate into the root folder
   of your PA installation. Run ``pip3 install -r requirements.txt --upgrade``.
   This will install and update the modules that PokeAlarm needs to run.

4. **Configure PokeAlarm** - Next you need to configure PokeAlarm.

   - :doc:`../configuration/server-settings` let you configure things like host
     IP, port, language, and more.
   - :doc:`../configuration/filters/index` represent which Events trigger
     notifications. You will need to create a filters file before starting PA.
   - :doc:`../configuration/alarms/index` represent where and how
     notifications. You will need to create an alarms file before starting PA.


Running
-------------------------------------

1. **Start PokeAlarm** - In a terminal, use the command
   ``python3 start_pokealarm.py`` to start PokeAlarm and begin listening for
   information. If successful, you will see the following in the output:

   .. code:: none

       PokeAlarm is listening for webhooks on: http://127.0.0.1:4000

.. note:: PokeAlarm installs some dependencies on the fly. If you encounter
   errors when first running a new service, try running as root (with `sudo`) to
   ensure it can install the dependency.

2. **Setup Scanner Webhook** - Next, configure your scanner to send information
   to PA's address.

   - **For MAD:**
     Configure the webhook types and URL to send info as explained in
     `MAD config.ini <https://github.com/Map-A-Droid/MAD/blob/master/configs/config.ini.example>`_.

   - **For RealDeviceMap:**
     Configure the webhook URL to send info as explained in
     `RealDeviceMap wiki <https://realdevicemap.readthedocs.io/en/latest/realdevicemap/dashboard/settings.html#webhook>`_.

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
3. Run the command ``git pull && pip3 install -r requirements.txt --upgrade``
   to update to the latest version.

.. |br| raw:: html
