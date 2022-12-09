'''
    Exceptions to be used when signaling errors from Barcodes associated Operations
'''

__all__ = [
    "ScanningFailureException",
]

class ScanningFailureException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
