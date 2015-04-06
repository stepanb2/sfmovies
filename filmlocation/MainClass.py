"""
Provides main class of this module - FilmLocation.
"""
from filmlocation.Exceptions import (
    FilmLocationBadConfigException, GoogleAddressApiException, FilmLocationApiException)
import hashlib
import json
import math
import random
import requests
import time


# fixme: move constants to the config file
# API URLS
GOOGLE_MAP_API_URL = "http://maps.googleapis.com/maps/api/geocode/json"
MOVIES_DATA_DOWNLOAD_URL = 'http://data.sfgov.org/resource/yitu-d5am.json'

# Redis namespace
FILM_NAMEPSPACE = "FilmNamespace"

# Wait time before next request to the Google Geocode Api
DEFAULT_SLEEP_TIME = 0.5

# MAX Number of returned responses
DEFAULT_COUNT_LIMIT = 50



# fixme: make the city related values configurable in the main class,
# to make it easy touse the module for another cities

# Coordinates of the SF city center
SF_CENTER_COORD = {
    "lat": 37.777,
    "lng": -122.444
}
DEFAULT_CITY = "San Francisco, CA, US"
# Used to filter out locations that are far away
DEFAULT_CITY_RADIUS = 20


DEFAULT_REQUIRED_FIELDS = [
    "id",
    "release_year",
    "title",
    "actor_1",
    "actor_2",
    "actor_3",
    "director",
    "production_company",
    "distributor",
    "lat",
    "lng",
    "locations"
]

DEFAULT_SEARCH_FIELDS = [
    "release_year",
    "title",
    "actor_1",
    "actor_2",
    "actor_3",
    "director",
    "production_company",
    "distributor"
]


def get_coordinates(address, city=DEFAULT_CITY):
    """
    :calls: GET {GOOGLE_MAP_API_URL}
    :rtype: object with the latitude and longitude coordinates
    """
    param = {"address": ','.join([address, city])}
    resp = requests.get(GOOGLE_MAP_API_URL, params=param)
    if resp.status_code != requests.codes.ok:
        raise GoogleAddressApiException(resp.status_code)
    data = resp.json()

    # returns None if data is empty
    if data["status"] == "ZERO_RESULTS":
        return None

    # check if the response data is correct
    if data["status"] != "OK":
        raise GoogleAddressApiException(resp.status_code, data)

    return data["results"][0]["geometry"]["location"]


def get_movies_data():
    """
    :calls: GET {MOVIES_DATA_DOWNLOAD_URL}
    :rtype: list of object
    """
    resp = requests.get(MOVIES_DATA_DOWNLOAD_URL)
    if resp.status_code != requests.codes.ok:
        raise FilmLocationApiException(resp.status_code, resp.text)
    return resp.json()


class FilmLocation(object):
    """
    This is the main class you instantiate to work with the film locations
    """

    def __init__(self, redis_db, cache_namespace=FILM_NAMEPSPACE, count=DEFAULT_COUNT_LIMIT):
        """
        :param redis_db: redis
        :param cache_namespace: string
        :param count: int
        """
        self._redis_db = redis_db
        self._cache_namespace = cache_namespace
        self._count = count
        assert redis_db

    def update_data(self, films, city=DEFAULT_CITY):
        """
        Add films to the Redis, also fetch lat/lng coordinates if they are not present
        Filter out films without locations and films that are already in the redis
        Fetches the film locations data and adds missing films to the db

        :param films: a list of json objects.
        :param city: string defines the city, for more accurate geocoding
        :rtype: number of added films

        Sample json object expected in this function:
        {
           "release_year":"1988",
           "title":"The Dead Pool",
           "writer":"Harry Julian Fink",
           "actor_1":"Clint Eastwood",
           "locations":"Hall of Justice (850 Bryant Street)",
           "actor_2":"Liam Neeson",
           "actor_3":"",
           "director":"Buddy Van Horn",
           "distributor":"Warner Bros. Pictures",
           "production_company":"Warner Bros. Pictures",
           "lat":37.775471, #optional
           "lng":-122.4037169, #optional
           "id":"6982b8fdb56fbe28fc1ebb9899131c37", #optional
        }
        """
        if films is None:
            return

        added = 0

        for film in films:
            if "id" not in film:
                # generate an id for each film
                # ignore films without locations, we won't be able to show them on the map
                if "locations" in film:
                    film["id"] = get_film_id(film)
                else:
                    continue
            # if the film has been already saved in db then just skip it
            if self._redis_db.hget(self._cache_namespace, film["id"]) is None:
                # Fetch coordinates if they are not present
                if "lat" not in film or "lng" not in film:
                    # make some delay, so Google won't ban the app
                    time.sleep(DEFAULT_SLEEP_TIME)
                    # fetch the latitude and longitude coordinates
                    coord = get_coordinates(film["locations"])
                    # skip the film with no coordinates
                    if coord is None:
                        continue
                    # Sometime Geocode API returns coordinates that are far away
                    dist = calc_distance(coord["lat"], coord["lng"],
                                         SF_CENTER_COORD["lat"], SF_CENTER_COORD["lng"])
                    if dist > DEFAULT_CITY_RADIUS:
                        continue
                    film["lat"] = coord["lat"]
                    film["lng"] = coord["lng"]
                # save an entry to the db
                self.add_film(film)
                added += 1
        return added


    def add_film(self, film):
        """
        Add film to the redis' films namespace.
        If some of the required fields is None, method changes it to default value.
        Do nothing if the object with the id already exists
        :param film film object
        """
        # sanity pre-process
        film = preprocess_data(film, DEFAULT_REQUIRED_FIELDS)
        if self._redis_db.hget(self._cache_namespace, film["id"]) is None:
            self._redis_db.hset(self._cache_namespace, film["id"], json.dumps(film))

    def remove_all_films(self):
        """
        Remove all films from redis
        """
        return self._redis_db.delete(self._cache_namespace)

    def remove_film(self, film_id):
        """
        Remove film by id from redis
        """
        return self._redis_db.hdel(self._cache_namespace, film_id)

    def _get_films_ids(self):
        """
        Get all films ids
        :rtype: list of the films ids
        """
        return self._redis_db.hkeys(self._cache_namespace)

    def _get_all_films(self):
        """
        Loads all films from the db
        :rtype: list of the films
        """
        return [self.get_film(idx) for idx in self._get_films_ids()]

    def get_random_films(self):
        """
        Returns random films from the db.
        :rtype: list of the films
        """
        # fixme : loads all ids, figure out something smarter
        ids = self._get_films_ids()
        random.shuffle(ids)
        films = [self.get_film(idx) for idx in ids[:self._count]]
        return films

    def get_film(self, film_id):
        """
        Lookups the film by the id
        :param film_id: string
        :rtype: the film object
        """
        json_film = self._redis_db.hget(self._cache_namespace, film_id)
        if json_film is not None:
            return json.loads(json_film)
        return None

    def _naive_search(self, query):
        """
        Returns the list of films that satisfy the query.
        :param all_films: list
        :param query: string
        :rtype: list of the films

        Naive implementation of the full text search.
        Since data size and growth rate are both small(around 1000 films) it's ok here.
        fixme: use Apache Solr(http://lucene.apache.org/solr) for the full text search instead
               or implement the custom indexing search
        """
        
        
        if query is None:
            return []
        # sanitize the query
        query = sanitize_query(query)
        if not query:
            return []

        # assumes that query is the list of tokens, takes only unique ones
        search_terms = list(set(query.lower().split(' ')))
        result = []
        # load films
        all_films = self._get_all_films()
        for film in all_films:
            found = set()
            for key in DEFAULT_SEARCH_FIELDS:
                if key not in film:
                    continue
                target = str(film[key]).lower()
                for search_term in search_terms:
                    if target.find(search_term) != -1:
                        found.add(search_term)
            # if all search terms are in the film object, add it to the result
            if len(found) == len(search_terms):
                result.append(film)
            # check if need to continue
            if len(result) == self._count:
                break
        return result

    def search(self, query):
        """
        Returns the list of films that satisfy the query.
        :param query: strings
        :rtype: list of the films
        """
        return self._naive_search(query)


# Utility functions
def calc_distance(lat1, long1, lat2, long2):
    """
    Calc distance between two points on the map
    """
    # Convert latitude and longitude to spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians

    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians

    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos(cos)

    # the radius of the earth in km
    radius = 6371
    distance = arc*radius
    return distance


def get_film_id(film):
    """
    Generates the id based on the film's title and the release year.
    Assuming the title/year/locations combination will be unique across all films.
    """
    value = "{}:{}:{}".format(
        film["title"].encode('ascii', 'ignore'),
        film["release_year"],
        film["locations"].encode('ascii', 'ignore')
    )
    return hashlib.md5(value).hexdigest()

def sanitize_query(query):
    """
    Sanitize query: strip, remove commas
    """
    query = query.strip().replace(',', '')
    return query

def preprocess_data(obj, required_fields, default=""):
    """
    Helper function that makes sure that all required fields are not None
    and set value to the default
    """
    for field in required_fields:
        val = obj.get(field)
        if val is None:
            obj[field] = default
    return obj
