#!/usr/bin/python
# -*- coding: utf-8 -*-

#Check for needed module, otherwise install 
try:
	import telepot
except ImportError:
	from ..utils import pip_install
	pip_install('telepot', '8.3')

from telegram_alarm import Telegram_Alarm