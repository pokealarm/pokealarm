import json
from quart import Quart, request


# Fill in app for development purposes
def create_app(test_config=None):
    # create and configure the app
    app = Quart(__name__)

    @app.route('/', methods=['GET'])
    async def hello():
        return "PokeAlarm v4 is running!"

    @app.route('/', methods=['POST'])
    async def receive_events():
        out = ""
        data = json.loads(await request.data)
        ct = 0
        for event in data:
            out += f'{ct}: {event}\n'
            ct += 1
        return out

    return app
