import requests

from Exceptions import FilmLocationApiException

MOVIES_DATA_DOWNLOAD_URL = 'http://data.sfgov.org/resource/yitu-d5am.json'

class FilmLocationLoader(object):
    """
        This is class you instanciate to access the Data SF API.
    """

    def __init__(self, base_url=MOVIES_DATA_DOWNLOAD_URL):
        """
        :param base_url string
        """
        assert isinstance(base_url, str), base_url

    def get_all(self):
        """
        :calls: GET {MOVIES_DATA_DOWNLOAD_URL}
        :rtype: list of object
        """
        r = requests.get(MOVIES_DATA_DOWNLOAD_URL)
        if r.status_code != requests.codes.ok:
            raise FilmLocationApiException(r.status_code)
        return r.json()


