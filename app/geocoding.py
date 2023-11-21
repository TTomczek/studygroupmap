import ssl
from functools import partial
from math import radians, cos, sin, degrees
import random

import certifi
import geopy
from geopy import Nominatim
from geopy.exc import GeocoderUnavailable
from geopy.extra.rate_limiter import RateLimiter

from app import app

geopy.geocoders.options.default_ssl_context = ctx = ssl.create_default_context(cafile=certifi.where())


def get_geocode():
    try:
        geolocator = Nominatim(user_agent="LerngruppenKarte", scheme="https")
        geocode_de = partial(geolocator.geocode, language="de")
        return RateLimiter(geocode_de, min_delay_seconds=3, max_retries=1, error_wait_seconds=5)
    except GeocoderUnavailable as e:
        app.logger.warning("Cannot update location. Geocoder is unavailable.", e)


def randomize_coordinates(lat, lon):
    # approximate radius of earth in km
    r = 6373.0

    # convert decimal degrees to radians
    lat = radians(lat)
    lon = radians(lon)

    # generate random distance between 50 and 200 meters
    distance = random.uniform(0.05, 0.2)

    # generate random angle between 0 and 360 degrees
    angle = random.uniform(0, 360)

    # calculate new coordinates
    lat_new = lat + (distance / r) * cos(radians(angle))
    lon_new = lon + (distance / (r * cos(lat))) * sin(radians(angle))

    # convert radians back to decimal degrees
    lat_new = degrees(lat_new)
    lon_new = degrees(lon_new)

    return lat_new, lon_new


def get_coordinates(address_string: str):

    if address_string is None:
        return None, None

    location = geocode(address_string)

    if location is None:
        return None, None

    return location.latitude, location.longitude


geocode = get_geocode()
