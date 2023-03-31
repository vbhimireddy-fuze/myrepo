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
    quality: int | None = None # Quality is just an indicator

    def __eq__(self, __value: object) -> bool:
        """
            Comparison operator.
            Barcode comparison only takes into account format and raw result,
              which is what truly identifies a barcode.
        """
        if not isinstance(__value, Barcode):
            return False
        if id(self) == id(__value):
            return True
        return self.format == __value.format and self.raw_result == __value.raw_result
