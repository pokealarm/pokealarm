#!/usr/bin/python
# -*- coding: utf-8 -*-

#Check for needed module, otherwise install 
try:
	import twitter
except ImportError:
	from ..utils import pip_install
	pip_install('twitter', '1.17.1')

from twitter_alarm import *