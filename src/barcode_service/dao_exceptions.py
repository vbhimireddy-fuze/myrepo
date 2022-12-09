'''
    Exceptions to be used when signaling errors from Database Operations
'''

__all__ = [
    "DaoException",
    "FailedInitializationException",
]

class DaoException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class FailedInitializationException(DaoException):
    pass
