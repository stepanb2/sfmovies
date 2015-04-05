from Exceptions import FilmLocationBadConfigException

import requests
import json
import redis
import filmlocation
import hashlib
import time


# Redis namespaces
FILM_NAMEPSPACE = "FilmNamespace"


INCREMENT_LOCK = "IncrementLock"

DEFAULT_COUNT_LIMIT = 50
DEFAULT_SLEEP_TIME = 0.5


class FilmLocation(object):
    """
    This is the main class you instantiate to work with the film locations
    """

    def __init__(self, redis_db, data_fetcher=None, coordinates_fetcher=None, count=DEFAULT_COUNT_LIMIT):
        self._redis_db = redis_db
        self._data_fetcher = data_fetcher
        self._coordinates_fetcher = coordinates_fetcher
        self._count = count
        assert redis_db

    def update_data(self):
        """
        Fetches the film locations data and adds missing films to the db
        """
        if self._data_fetcher is None or self._coordinates_fetcher is None:
            raise FilmLocationBadConfigException("Incomplete Config", "data_fetcher and/or coordinates_fetcher is None")
        films = self._data_fetcher.get_all()
        for film in films:
            # generate an id for each film
            # ignore films without locations, we won't be able to show them on the map
            if "locations" in film:
                film["id"] = get_film_id(film)
            else:
                continue
            # if the film has been already saved in db then just skip it
            if self._redis_db.hget(FILM_NAMEPSPACE, film["id"]) is None:
                # make some delay, so Google won't ban the app
                time.sleep(DEFAULT_SLEEP_TIME)
                # fetch the latitude and longitude coordinates
                coordinates = self._coordinates_fetcher.get_coordinates(film["locations"])
                # skip the film with no coordinates
                if coordinates is None:
                    continue
                film["lat"] = coordinates["lat"]
                film["lng"] = coordinates["lng"]
                # it's a new film, set the popularity to 0
                film["rating"] = 0
                # save an entry to the db
                self._redis_db.hset(FILM_NAMEPSPACE, film["id"], json.dumps(film))


    def _get_films_ids(self):
        """
        Get all films ids
        """
        ids = self._redis_db.hkeys(FILM_NAMEPSPACE)
        return ids

    def _get_all_films(self):
        """
        Loads all films from the db
        """
        ids = self._get_films_ids()
        films = [self.get_film(idx) for idx in ids]
        return films

    def get_most_popular(self):
        """
        Returns most popular films in the db
        """
        films = self._get_all_films()
        result = sorted(films, key=lambda x: x["rating"], reverse=True)
        return result[:self._count]

    def get_film(self, film_id):
        """
        Lookups the film by the id
        """
        json_film = self._redis_db.hget(FILM_NAMEPSPACE, film_id)
        return json.loads(json_film)

    def increase_rating(self, film_id, increment=1):
        """
        Increase rating for the film
        """
        # Naive usage of the lock, ideally the non-blocking update should be used
        with self._redis_db.lock(INCREMENT_LOCK):
            film = self.get_film(film_id)
            film["rating"] += increment
            self._redis_db.hset(FILM_NAMEPSPACE, film_id, json.dumps(film))

    def _naive_search(self, all_films, query):
        """
        Returns the list of films that satisfy the query.
        Naive implementation of the full text search.
        Since data size and growth rate are both small it's ok here.
        """
        # rank the films by rating
        all_films = sorted(all_films, key=lambda x: x["rating"], reverse=True)
        result = []
        # assumes that query is the list of tokens, takes only unique ones
        search_terms = list(set(query.lower().split(' ')))
        for film in all_films:
            found = set()
            for key, value in film.iteritems():
                # skip id field
                if key == "id":
                    continue
                # also skip non text fields like latitude and longitude
                if type(value) is str or type(value) is unicode:
                    target = value.lower()
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
        The return list is ranked by popularity.
        """
        all_films = self._get_all_films()
        films = self._naive_search(all_films, query)
        return films


def get_film_id(film):
    """
    Generates the id based on the film's title and the release year.
    Assuming the title/year/locations combination will be unique across all films.
    """
    s = "{}:{}:{}".format(
        film["title"].encode('ascii','ignore'),
        film["release_year"],
        film["locations"].encode('ascii','ignore')
    )
    return hashlib.md5(s).hexdigest()

