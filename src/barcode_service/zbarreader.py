# coding=utf-8
import logging
from pathlib import Path
from typing import Generator, Tuple

from PIL import Image, ImageSequence, UnidentifiedImageError
from pyzbar.pyzbar import PyZbarError
from pyzbar.pyzbar import decode as pyzbar_decode

from barcode_service.processing_exceptions import ScanningFailureException

__all__ = [
    "zbar_barcode_extractor"
]

_log = logging.getLogger(__name__)


def zbar_barcode_extractor(image_location: Path) -> Generator[Tuple[int, str, str], None, None]:
    try:
        images = Image.open(str(image_location.absolute()), mode = 'r')
    except (UnidentifiedImageError, FileNotFoundError) as ex:
        raise ScanningFailureException(f"Cannot process image at location [{image_location.absolute()}]") from ex

    for image_page, image in enumerate(ImageSequence.Iterator(images), start=1):
        try:
            for result in pyzbar_decode(image):
                data_type: str = result.type
                data = result.data
                data = data.decode("utf-8") if isinstance(data, bytes) else str(data)
                _log.debug(f"Yielding barcode information: image page [{image_page}]; data type [{data_type}]; value [{data}]")
                yield (image_page, data_type, data)
        except PyZbarError as ex:
            _log.error(f"Failed to process image at page [{image_page}] due to: [{str(ex)}]")
