"""
pokealarmv4.webviews.general
~~~~~~~~~~~~~~~~

This module contains the blueprint for receiving and processing info.
"""

import json
from quart import Blueprint, request

general = Blueprint('general', __name__)


@general.route('/', methods=['GET'])
async def hello():
    return "PokeAlarm v4 is running!"


@general.route('/', methods=['POST'])
async def receive_events():
    out = ""
    data = json.loads(await request.data)
    ct = 0
    for event in data:
        out += f'{ct}: {event}\n'
        ct += 1
    return out
