"""
Script updates the film location data.
"""
import redis
import filmlocation


def main():
    redis_db = redis.Redis(host='localhost', port=6379)
    raw_data = filmlocation.get_movies_data()

    film_lib = filmlocation.FilmLocation(redis_db)
    added = film_lib.update_data(raw_data)
    print added


if __name__ == "__main__":
    main()