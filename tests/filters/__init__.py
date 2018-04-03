import logging


class MockManager(object):
    """ Mock manager for filter unit testing. """
    def get_child_logger(self, name):
        return logging.getLogger('test').getChild(name)
