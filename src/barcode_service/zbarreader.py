# coding=utf-8
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Generator, Tuple

from PIL import Image, ImageFilter, ImageSequence, UnidentifiedImageError
from pyzbar.pyzbar import PyZbarError
from pyzbar.pyzbar import decode as pyzbar_decode

from barcode_service.processing_exceptions import ScanningFailureException

# Pillow Filters -> https://pillow.readthedocs.io/en/stable/reference/ImageFilter.html
_USING_FILTERS = (
    ImageFilter.GaussianBlur(1),
)

__all__ = [
    "zbar_barcode_extractor"
]

_log = logging.getLogger(__name__)

@dataclass
class ZBarBarcode():
    data_type: str
    data: str
    quality: int

    def __hash__(self) -> int:
        return hash(f"{self.quality:d}{self.data_type:s}{self.data:s}")


def _update_barcode_with_highest_quality(barcodes_set: set[ZBarBarcode], barcode_compare: ZBarBarcode):
    barcode_to_remove: ZBarBarcode | None = None
    found: bool = False
    for barcode in barcodes_set:
        if barcode.data == barcode_compare.data and barcode.data_type == barcode_compare.data_type:
            if barcode.quality < barcode_compare.quality:
                barcode_to_remove = barcode
            found = True
            break

    if found:
        if barcode_to_remove:
            barcodes_set.remove(barcode_to_remove)
            barcodes_set.add(barcode_compare)
    else:
        barcodes_set.add(barcode_compare)


def _zbar_decode_barcodes(image: Image.Image) -> Generator[ZBarBarcode, None, None]:
    for result in pyzbar_decode(image):
        yield ZBarBarcode(
            data_type=result.type,
            data=result.data.decode("utf-8") if isinstance(result.data, bytes) else str(result.data),
            quality=result.quality
        )


def zbar_barcode_extractor(image_location: Path) -> Generator[Tuple[int, str, str, int], None, None]:
    try:
        images = Image.open(str(image_location.absolute()), mode = 'r')
    except (UnidentifiedImageError, FileNotFoundError) as ex:
        raise ScanningFailureException(f"Cannot process image at location [{image_location.absolute()}]") from ex

    for image_page, image in enumerate(ImageSequence.Iterator(images), start=1):
        try:
            image = image.convert('L')
            barcodes_results: set[ZBarBarcode] = set(_zbar_decode_barcodes(image))
            _log.info(f"Barcodes set from original image at page [{image_page}]: [{len(barcodes_results)}] - [{barcodes_results}] - file [{image_location}]")
            for image_filter in _USING_FILTERS:
                filtered_image = image.filter(image_filter)
                for barcode in _zbar_decode_barcodes(filtered_image):
                    _update_barcode_with_highest_quality(barcodes_results, barcode)

            _log.info(f"Final barcodes set after image enhancement at page [{image_page}]: [{len(barcodes_results)}] - [{barcodes_results}] - file [{image_location}]")
            for barcode in barcodes_results:
                _log.debug(
                    f"Yielding barcode information: "
                    f"image page [{image_page}]; data type [{barcode.data_type}]; "
                    f"value [{barcode.data}]; quality [{barcode.quality}]"
                )
                yield (image_page, barcode.data_type, barcode.data, barcode.quality)
        except PyZbarError as ex:
            _log.error(f"Failed to process image at page [{image_page}] due to: [{str(ex)}]")
