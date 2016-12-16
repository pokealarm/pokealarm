#!/usr/bin/python
# -*- coding: utf-8 -*-

#Check for needed module, otherwise install 
try:
	import facebook
except ImportError:
	from ..utils import pip_install
	pip_install('facebook-sdk', '2.0.0')

from facebookpages_alarm import FacebookPages_Alarm