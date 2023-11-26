import ssl
from functools import partial
from math import radians, cos, sin, degrees
import random

import certifi
import geopy
from geopy import Nominatim, distance
from geopy.exc import GeocoderUnavailable
from geopy.extra.rate_limiter import RateLimiter

from app import app

geopy.geocoders.options.default_ssl_context = ctx = ssl.create_default_context(cafile=certifi.where())


def get_geocode():
    """Gibt eine Funktion zurück, die eine Adresse in Koordinaten umwandelt."""
    try:
        geolocator = Nominatim(user_agent="LerngruppenKarte", scheme="https")
        geocode_de = partial(geolocator.geocode, language="de")
        return RateLimiter(geocode_de, min_delay_seconds=3, max_retries=1, error_wait_seconds=5)
    except GeocoderUnavailable as e:
        app.logger.warning("Cannot update location. Geocoder is unavailable.", e)


def randomize_coordinates(lat, lon):
    """Generiert zufällige Koordinaten in der Nähe der übergebenen Koordinaten.
    Die Koorianten befinden sich in einem Umkreis von 50 bis 200 Metern."""
    r = 6373.0

    lat = radians(lat)
    lon = radians(lon)

    distance = random.uniform(0.05, 0.2)

    angle = random.uniform(0, 360)

    lat_new = lat + (distance / r) * cos(radians(angle))
    lon_new = lon + (distance / (r * cos(lat))) * sin(radians(angle))

    lat_new = degrees(lat_new)
    lon_new = degrees(lon_new)

    return lat_new, lon_new


def get_coordinates(address_string: str):
    """Gibt die Koordinaten einer Adresse zurück."""
    if address_string is None:
        return None, None

    location = geocode(address_string)

    if location is None:
        return None, None

    return location.latitude, location.longitude


def get_distance_between_coords(lat1, lon1, lat2, lon2):
    """Gibt die Distanz zwischen zwei Koordinaten in Kilometer zurück."""
    return distance.distance((lat1, lon1), (lat2, lon2)).km


geocode = get_geocode()
