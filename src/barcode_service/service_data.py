'''
    Data structures used by this service
'''

from dataclasses import dataclass

__all__ = [
    "Barcode",
]

@dataclass
class Barcode():
    page_no: int
    format: str
    raw_result: str
