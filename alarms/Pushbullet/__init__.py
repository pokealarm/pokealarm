#!/usr/bin/python
# -*- coding: utf-8 -*-

#Check for needed module, otherwise install 
try:
	import pushbullet
except ImportError:
	from ..utils import pip_install
	pip_install('pushbullet.py', '0.10.0')

from pushbullet_alarm import Pushbullet_Alarm