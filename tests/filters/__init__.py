import logging


class MockManager(object):
    """ Mock manager for filter unit testing. """
    def get_child_logger(self, name):
        return logging.getLogger('test').getChild(name)


def generic_filter_test(test):
    """Decorator used for creating a generic filter test.

    Requires the argument to be a function that assigns the following
    attributes when called:
    filt = dict used to generate the filter,
    event_key = key for the event values,
    pass_vals = values that create passing events,
    fail_vals = values that create failing events
    """
    test(test)

    def generic_test(self):
        # Create the filter
        filt = self.gen_filter(test.filt)
        # Test passing
        for val in test.pass_vals:
            event = self.gen_event({test.event_key: val})
            self.assertTrue(
                filt.check_event(event),
                "pass_val failed check in {}: \n{} passed {}"
                "".format(test.__name__, event, filt))
        # Test failing
        for val in test.fail_vals:
            event = self.gen_event({test.event_key: val})
            self.assertFalse(
                filt.check_event(event),
                "fail_val  passed check in {}: \n{} passed {}"
                "".format(test.__name__, event, filt))
    return generic_test
