import redis
import filmlocation


def main():
    pool = redis.ConnectionPool(host='localhost', port=6379)
    redis_db = redis.Redis(connection_pool=pool)
    data_fetcher = filmlocation.FilmLocationLoader()
    coordinates_fetcher = filmlocation.CoordinatesLoader()
    print 'start'
    manager = filmlocation.FilmLocation(redis_db, data_fetcher, coordinates_fetcher)
    manager.update_data()
    print 'finish'


if __name__ == "__main__":
    main()