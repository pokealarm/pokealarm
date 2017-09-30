import signal


# Attachable object to try and make processes stop gracefully
class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    # Flag that we want to kill the process
    def exit_gracefully(self, signum, frame):
        self.kill_now = True
