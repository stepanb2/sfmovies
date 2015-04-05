class BaseException(Exception):
    """
    This class is the base of all exceptions raised in this module.
    """

    def __init__(self, status, data):
        message = "{}:{}".format(status, data)
        Exception.__init__(self, message)
        self.__status = status
        self.__data = data

    @property
    def status(self):
        """
        The error status
        """
        return self.__status

    @property
    def data(self):
        """
        The additional data associated with the exception
        """
        return self.__data


class FilmLocationApiException(BaseException):
    """
    Exception raised in case of the error during accessing a film location API
    """
    pass


class GoogleAddressApiException(BaseException):
    """
    Exception raised in case of the error during accessing the Google Map API
    """
    pass

class FilmLocationBadConfigException(BaseException):
    """
    Exception raised in case of the bad configuration
    """
    pass