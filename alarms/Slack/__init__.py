#!/usr/bin/python
# -*- coding: utf-8 -*-

#Check for needed module, otherwise install 
try:
	import slacker
except ImportError:
	from ..utils import pip_install
	pip_install('slacker', '0.9.24')

from slack_alarm import *