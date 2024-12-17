from pathlib import Path

from PIL import Image, TiffImagePlugin
from PIL.ExifTags import GPSTAGS, IFD, TAGS

from .base import InfoValue


class ImageResearcher:
    """
    A class to perform research operations on image files.
    """

    @staticmethod
    def accepts(file: Path) -> bool:
        return file.suffix.lower() in {
            ".jpg",
            ".png",
            ".jpeg",
            ".gif",
            ".bmp",
            ".tiff",
            ".webp",
        }

    def get_info(self, file: Path) -> dict[str, InfoValue]:
        with Image.open(file) as img:
            width, height = img.size
            xres, yres = img.info.get("dpi", (None, None))
            exif = {f"exif:{k}": v for k, v in self.__get_exif_as_dict(img).items()}

        return {
            "width": width,
            "height": height,
            "xres": float(xres) if xres else None,
            "yres": float(yres) if yres else None,
            **exif,
        }

    @staticmethod
    def __get_exif_as_dict(img: Image.Image) -> dict[str, InfoValue]:
        # https://stackoverflow.com/a/75357594
        exif = img.getexif()
        exif_tags = {TAGS.get(k, f"unknown_exif_{k}"): cast_exif(v) for k, v in exif.items()}

        for ifd_id in IFD:
            try:
                ifd = exif.get_ifd(ifd_id)

                if ifd_id == IFD.GPSInfo:
                    resolve = GPSTAGS
                else:
                    resolve = TAGS

                for k, v in ifd.items():
                    tag = resolve.get(k, str(k))
                    exif_tags[tag] = cast_exif(v)

            except KeyError:
                pass

        return exif_tags  # type: ignore


def cast_exif(v):
    """
    Recursively casts EXIF data to appropriate Python types.

    This function handles various types of EXIF data, converting them to more
    usable Python types:
    - TiffImagePlugin.IFDRational instances are converted to floats.
    - Tuples are recursively processed to cast their elements.
    - Byte strings are decoded to regular strings with error replacement.
    - Dictionaries are recursively processed to cast their values.

    Source: https://github.com/python-pillow/Pillow/issues/6199#issuecomment-1214854558

    Args:
        v: The EXIF data to be cast, which can be of various types including
           TiffImagePlugin.IFDRational, tuple, bytes, or dict.

    Returns:
        The casted EXIF data, with types converted as described above.
    """
    if isinstance(v, TiffImagePlugin.IFDRational):
        return float(v)
    elif isinstance(v, tuple):
        return tuple(cast_exif(t) for t in v)
    elif isinstance(v, bytes):
        return v.decode(errors="replace")
    elif isinstance(v, dict):
        for kk, vv in v.items():
            v[kk] = cast_exif(vv)
        return v
    else:
        return v
