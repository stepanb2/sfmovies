import unittest
import filmlocation
import redis


FILMS = [
    {
        "rating":0,
        "release_year":"2014",
        "title":"Looking",
        "writer":"Michael Lannan",
        "actor_1":"Jonathan Groff",
        "locations":"Mission Arts Center",
        "actor_3":"Murray Bartlett",
        "actor_2":"Frankie J. Alvarez",
        "director":"Andrew Haigh",
        "distributor":"Home Box Office (HBO)",
        "production_company":"Mission Street Producitons, LLC",
        "lat":37.7509895,
        "lng":-122.4186484,
        "id":"044f30613cd2db03c95864b1bfed4ae1"
    },
    {  
       "rating":0,
       "release_year":"1988",
       "title":"The Dead Pool",
       "writer":"Harry Julian Fink",
       "actor_1":"Clint Eastwood",
       "locations":"Hall of Justice (850 Bryant Street)",
       "actor_2":"Liam Neeson",
       "director":"Buddy Van Horn",
       "distributor":"Warner Bros. Pictures",
       "production_company":"Warner Bros. Pictures",
       "lat":37.775471,
       "lng":-122.4037169,
       "id":"6982b8fdb56fbe28fc1ebb9899131c37"
    },
    {  
       "rating":0,
       "release_year":"1983",
       "title":"Sudden Impact",
       "writer":"Harry Julian Fink",
       "actor_1":"Clint Eastwood",
       "locations":"Pier 38-40, The Embarcadero",
       "actor_3":"Artie Lang",
       "actor_2":"Sondra Locke",
       "director":"Clint Eastwood",
       "distributor":"Warner Bros. Pictures",
       "production_company":"Warner Bros. Pictures",
       "lat":37.7825065,
       "lng":-122.387181,
       "id":"65a70047cd53f4d9fcc8ca8dc78856c7"
    }
]


# fixme: add more tests

class UpdateDataTestCase(unittest.TestCase):

    def setUp(self):
        # fixme: use separate redis instance for testing
        redis_db = redis.Redis(host='localhost', port=6379)
        self.film_lib = filmlocation.FilmLocation(redis_db, cache_namespace="TestFilmLocations")

    def tearDown(self):
        # clean data
        self.film_lib.remove_all_films()

    def testUpdateData(self):
        self.film_lib.update_data(FILMS)
        all_films = self.film_lib._get_all_films()
        self.assertEqual(len(all_films), len(FILMS))


class BasicSearchTestCase(unittest.TestCase):

    def setUp(self):
        # fixme: use separate redis instance for testing
        redis_db = redis.Redis(host='localhost', port=6379)
        self.film_lib = filmlocation.FilmLocation(redis_db, cache_namespace="TestFilmLocations")
        self.film_lib.update_data(FILMS)

    def tearDown(self):
        # clean data
        self.film_lib.remove_all_films()

    def testSearch(self):
        result = self.film_lib.search("Jonathan Groff")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "044f30613cd2db03c95864b1bfed4ae1")

    def testnNoneSearch(self):
        result = self.film_lib.search(None)
        self.assertEqual(len(result), 0)

    def testnGetRandom(self):
        result = self.film_lib.get_random_films()
        self.assertEqual(len(result), 3)


class TestApiTestCase(unittest.TestCase):

    def testCoordinateslookUp(self):
        coord = filmlocation.get_coordinates(FILMS[0]["locations"])
        self.assertEqual(coord["lat"], FILMS[0]["lat"])
        self.assertEqual(coord["lng"], FILMS[0]["lng"])

    def testDistance(self):
        dist = filmlocation.calc_distance(FILMS[0]["lat"], FILMS[0]["lng"], FILMS[1]["lat"], FILMS[1]["lng"])
        self.assertEqual(int(dist), 3)


if __name__ == '__main__':
    unittest.main()