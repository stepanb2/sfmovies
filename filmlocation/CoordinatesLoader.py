import requests

from Exceptions import GoogleAddressApiException

DEFAULT_CITY = "San Francisco"
DEFAULT_STATE = "CA"
GOOGLE_MAP_API_URL = "http://maps.googleapis.com/maps/api/geocode/json"


class CoordinatesLoader(object):
    """
        This is class you instanciate to access the Google Map API to fetch
        the latitude and longitude by the address.
    """

    def __init__(self, base_url=GOOGLE_MAP_API_URL):
        """
        :param base_url string
        """
        assert isinstance(base_url, str), base_url

    def get_coordinates(self, address, city=DEFAULT_CITY, state=DEFAULT_STATE):
        """
        :calls: GET {GOOGLE_MAP_API_URL}
        :rtype: object with the latitude and longitude coordinates
        """
        params = {"address": address, "city": city, "state": state}
        r = requests.get(GOOGLE_MAP_API_URL, params=params)
        if r.status_code != requests.codes.ok:
            raise GoogleAddressApiException(r.status_code)
        data = r.json()

        # returns None if data is empty
        if data["status"] == "ZERO_RESULTS":
            return None

        # check if the response data is correct
        if data["status"] != "OK":
            raise GoogleAddressApiException(r.status_code, data)

        return data["results"][0]["geometry"]["location"]
