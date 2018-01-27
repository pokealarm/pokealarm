# Installation

## Overview

This guide will walk you through the initial setup of PokeAlarm.

* [Prerequisites](#prerequisites)
* [Installation](#installation)
* [Running PokeAlarm](#running-pokealarm)
* [Updating PokeAlarm](#updating-pokealarm)

## Prerequisites

This guide assumes the following:

1. You have [Python 2.7](https://www.python.org/download/releases/2.7/)
  successfully installed
2. You have [Git](https://git-scm.com/downloads) successfully installed
3. You have [RocketMap](https://github.com/RocketMap/RocketMap) or another
  supported scanner successfully installed.
4. You have either Notepad++, Nano, or Vi(m) installed. Do **NOT** use or
  open any files with Notepad or TextEdit - they will break your files!

## Installation

1. **Clone PokeAlarm locally** - Create a new folder to install PokeAlarm (it
  is recommended you store it in a different folder than your scanner). Use
  `git clone https://github.com/PokeAlarm/PokeAlarm.git` to create a local
  copy of the project.

2. **Install requirements** - Navigate into the root folder of your PokeAlarm
  installation. Run `pip install -r requirements.txt --upgrade`.
  This will install and update the packages that PokeAlarm needs to run.

3. **Create your Filters configuration file** - Copy and paste
  `alarms.json.example`. Rename the copy to `alarms.json`. This file will
  tell PokeAlarm what information it should send.

4. **Create your Alarms configuration file** - Copy and paste
  `filters.json.example`. Rename the copy to `filters.json`. This file will
  tell PokeAlarm what the alerts to say and what service to send them on.

5. **Finish configuring PokeAlarm** - Now you should configure PokeAlarm.
  Use the [Configuration Guide](started-guide) for more detailed instructions
  on how to personalize PokeAlarm to fit your needs.


## Running PokeAlarm

1. **Start PokeAlarm** - Run the command `python start_pokealarm.py` to
  have PokeAlarm start and begin listening for information via webhooks.
 **Note:** PokeAlarm installs some dependencies on the fly. If you encounter
  errors when first running a new service, try running as root (with `sudo`)
  to insure it can install the dependency.

2. **Send webhooks to PokeAlarm** - Make sure you are sending your webhooks
  to PokeAlarm by adding PokeAlarm's address to your scanner. If you are using
  RocketMap (and the default PokeAlarm settings), add
  `-wh http://127.0.0.1:4000` to your start up command or
  `webhook:http://127.0.0.1:4000` to your `config.ini` file.

## Updating PokeAlarm
Updating PokeAlarm is a simple process, provided you haven't changed any
files you weren't supposed to. For this reason, it is highly suggested not
to edit any files that end in the `.py` extension.
1. Open a command line in the root folder of your PokeAlarm installation.
2. Run `git pull`.
3. Run `pip install -r requirements.txt`.
4. Make sure to checkout the [Patch Notes](patch-notes) to see if any updates
  to your config files are necessary.
