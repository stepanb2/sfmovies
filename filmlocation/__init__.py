"""
The module provides utilities  to work moview locations.
Like downloading, fetching map's coordinates, storing in redis.
The primary class you will instanciate is :class:`filmlocation.MainClass.FilmLocation`.
"""
from filmlocation.Exceptions import (
    FilmLocationApiException, GoogleAddressApiException, FilmLocationBadConfigException)
from filmlocation.MainClass import FilmLocation, get_movies_data, get_coordinates, calc_distance

VERSION = "0.0.1"
