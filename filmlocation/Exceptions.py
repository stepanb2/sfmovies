"""
Exceptions definition for the film location module.
"""

class FilmBaseException(Exception):
    """
    This class is the base of all exceptions raised in this module.
    """

    def __init__(self, status, data):
        message = "{}:{}".format(status, data)
        super(FilmBaseException, self).__init__(message)
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


class FilmLocationApiException(FilmBaseException):
    """
    Exception raised in case of the error during accessing a film location API
    """
    pass


class GoogleAddressApiException(FilmBaseException):
    """
    Exception raised in case of the error during accessing the Google Map API
    """
    pass

class FilmLocationBadConfigException(FilmBaseException):
    """
    Exception raised in case of the bad configuration
    """
    pass
