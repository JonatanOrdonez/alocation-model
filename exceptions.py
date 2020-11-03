class Error(Exception):
    """Base class for other exceptions"""
    pass


class InvalidArrayShape(Error):
    """Raised when the array input has a wrong shape"""
    pass