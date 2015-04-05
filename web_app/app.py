from flask import Flask, make_response

import filmlocation
import json
import redis
import requests


MOST_POPULAR_NAMESPACE = "MostPopularFilms"
SEARCH_CACHE_NAMESPACE = "SearchCache"
DEFAULT_CACHE_EXPIRATION = 60*60

# Web App setup
app = Flask(__name__)

# Redis setup
pool = redis.ConnectionPool(host='localhost', port=6379)
redis_db = redis.Redis(connection_pool=pool)

# Film location lib setup
filmlib = filmlocation.FilmLocation(redis_db)


@app.route("/api/locations/most_popular")
def get_popular_locations():
    # check in the cache first
    result = redis_db.get(MOST_POPULAR_NAMESPACE)
    if result is None:
        # otherwise take from the db
        films = filmlib.get_most_popular()
        result = json.dumps(films)
    # set result to the cache
    redis_db.set(MOST_POPULAR_NAMESPACE, result)
    # set expiration
    redis_db.expire(MOST_POPULAR_NAMESPACE, DEFAULT_CACHE_EXPIRATION)
    return make_response(result, 200)


@app.route("/api/locations/search/<string:query>", methods=["GET"])
def get_search_result(query):
    # check cache first
    result = redis_db.hget(SEARCH_CACHE_NAMESPACE, query)
    if result is not None:
        ids = json.loads(result)
        result = [filmlib.get_film(idx) for idx in ids]
    else:
        # otherwise take from the db
        result = filmlib.search(query)
    # set result to the cache, cache films ids only
    ids = [film["id"] for film in result]
    redis_db.hset(SEARCH_CACHE_NAMESPACE, query, json.dumps(ids))
    # set expiration
    redis_db.expire(MOST_POPULAR_NAMESPACE, DEFAULT_CACHE_EXPIRATION)
    return make_response(json.dumps(result), 200)


@app.route("/api/locations/rate/<string(length=32):film_id>", methods=["POST"])
def rate_film(film_id):
    filmlib.increase_rating(film_id)
    return make_response(json.dumps({'status': 'Done.'}), 200)


@app.errorhandler(404)
def not_found(error):
    return make_response(json.dumps({'error': 'Not found'}), 404)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
