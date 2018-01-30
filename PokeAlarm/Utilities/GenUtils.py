# Standard Library Imports
# 3rd Party Imports
# Local Imports


def parse_bool(value):
    try:
        b = str(value).lower()
        if b in {'t', 'true', 'y', 'yes'}:
            return True
        if b in {'f', 'false', 'n', 'no'}:
            return False
    except Exception:
        pass  # Skip below
    raise ValueError('Not a valid boolean')
