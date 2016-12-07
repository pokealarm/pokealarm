#!/usr/bin/python
# -*- coding: utf-8 -*-

#Check for needed module, otherwise install 
try:
    import requests
except ImportError:
	from ..utils import pip_install
	pip_install('requests')
	
from discord_alarm import *
