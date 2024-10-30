from pathlib import Path

from PIL import Image
from PIL.ExifTags import GPSTAGS, IFD, TAGS

from .base import InfoValue


class ImageResearcher:
    """
    A class to perform research operations on image files.
    """

    def accepts(self, file: Path) -> bool:
        return file.suffix.lower() in {".jpg", ".png", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"}

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
        exif_tags = {TAGS.get(k, f"unknown_exif_{k}"): v for k, v in exif.items()}

        for ifd_id in IFD:
            try:
                ifd = exif.get_ifd(ifd_id)

                if ifd_id == IFD.GPSInfo:
                    resolve = GPSTAGS
                else:
                    resolve = TAGS

                for k, v in ifd.items():
                    tag = resolve.get(k, str(k))
                    exif_tags[tag] = v

            except KeyError:
                pass

        return exif_tags
