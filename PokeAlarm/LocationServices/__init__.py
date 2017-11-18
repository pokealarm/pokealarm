from GoogleMaps import GoogleMaps


def location_service_factory(kind, api_key, locale, units):
    if kind == "GoogleMaps":
        return GoogleMaps(api_key, locale, units)
    else:
        raise ValueError(
            "%s is not a valid location service!".format(kind))
