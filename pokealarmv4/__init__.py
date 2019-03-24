from quart import Quart
from .webviews import general


# Creates a runnable app
def create_app(test_config=None):
    # create and configure the app
    app = Quart(__name__)
    app.register_blueprint(general)

    return app
