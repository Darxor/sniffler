from pathlib import Path
from typing import Any, Protocol

from PIL import Image
from PIL.ExifTags import GPSTAGS, IFD, TAGS


class Researcher(Protocol):
    def accepts(self, file: Path) -> bool: ...

    def get_info(self, file: Path) -> dict[str, Any]: ...


class BasicResearcher:
    def accepts(self, file: Path) -> bool:
        return True

    def get_info(self, file: Path) -> dict[str, Any]:
        return {"name": file.name, "size": file.stat().st_size}


class ImageResearcher:
    def accepts(self, file: Path) -> bool:
        return file.suffix.lower() in {".jpg", ".png", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"}

    def get_info(self, file: Path) -> dict[str, Any]:
        with Image.open(file) as img:
            width, height = img.size
            xres, yres = img.info.get("dpi", (None, None))
            exif = {f"exif:{k}": v for k, v in self.__get_exif_as_dict(img).items()}

        return {"width": width, "height": height, "xres": xres, "yres": yres, **exif}

    @staticmethod
    def __get_exif_as_dict(img: Image.Image) -> dict[str, Any]:
        # https://stackoverflow.com/a/75357594
        exif = img.getexif()
        exif_tags = {TAGS[k]: v for k, v in exif.items()}

        for ifd_id in IFD:
            try:
                ifd = exif.get_ifd(ifd_id)

                if ifd_id == IFD.GPSInfo:
                    resolve = GPSTAGS
                else:
                    resolve = TAGS

                for k, v in ifd.items():
                    tag = resolve.get(k, k)
                    exif_tags[tag] = v

            except KeyError:
                pass

        return exif_tags
