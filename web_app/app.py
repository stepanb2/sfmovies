"""
Flask web app defines the api handlers for the Film Locations in San Francisco web site.
"""
from flask import Flask, make_response, request

import filmlocation
import json
import redis


SEARCH_CACHE_NAMESPACE = "SearchCache"
RANDOM_REQUEST_KEY = "RandomCache"
DEFAULT_CACHE_EXPIRATION = 60*60

# Web App setup
app = Flask(__name__)

# Redis setup
pool = redis.ConnectionPool(host='localhost', port=6379)
redis_db = redis.Redis(connection_pool=pool)

# Film location lib setup
film_lib = filmlocation.FilmLocation(redis_db)

# fixme: use Flask-Cache decorators
@app.route("/api/locations/explore")
def get_random_locations():
    """
    Handles /api/locations/explore API calls
    Makes result caching
    """
    # check cache first
    result = redis_db.get(RANDOM_REQUEST_KEY)
    if result is not None:
        return result
    # otherwise take from the db
    result = film_lib.get_random_films()
    redis_db.set(RANDOM_REQUEST_KEY, json.dumps(result))
    # set expiration
    redis_db.expire(RANDOM_REQUEST_KEY, DEFAULT_CACHE_EXPIRATION)
    return make_response(json.dumps(result), 200)

# fixme: use Flask-Cache decorators
@app.route("/api/locations/search/", methods=["GET"])
def get_search_result():
    """
    Handles /api/locations/search API calls
    Makes result caching
    """
    query = request.args.get('q')
    # check cache first
    result = redis_db.hget(SEARCH_CACHE_NAMESPACE, query)
    if result is not None:
        ids = json.loads(result)
        result = [film_lib.get_film(idx) for idx in ids]
    else:
        # otherwise take from the db
        result = film_lib.search(query)
    # set result to the cache, cache films ids only
    ids = [film["id"] for film in result]
    redis_db.hset(SEARCH_CACHE_NAMESPACE, query, json.dumps(ids))
    # set expiration
    redis_db.expire(SEARCH_CACHE_NAMESPACE, DEFAULT_CACHE_EXPIRATION)
    return make_response(json.dumps(result), 200)


@app.errorhandler(404)
def not_found():
    """
    Handles not found responses
    """
    return make_response(json.dumps({'error': 'Not found'}), 404)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
