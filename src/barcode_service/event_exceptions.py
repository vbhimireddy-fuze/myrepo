'''
    Exceptions to be used when signaling errors from Events Operations
'''

__all__ = [
    "InvalidMessageAttributeException",
]

class InvalidMessageAttributeException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
