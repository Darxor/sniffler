from pathlib import Path

from tinytag import TinyTag

from .base import InfoValue


class AudioResearcher:
    """
    A class to perform research operations on audio files.
    """

    def accepts(self, file: Path) -> bool:
        return file.suffix.lower() in set(TinyTag.SUPPORTED_FILE_EXTENSIONS)

    def get_info(self, file: Path) -> dict[str, InfoValue]:
        tag = TinyTag.get(file, ignore_errors=True)

        return {
            "title": tag.title,
            "artist": tag.artist,
            "album": tag.album,
            "duration": tag.duration,
            "bitrate": tag.bitrate,
            "samplerate": tag.samplerate,
            "channels": tag.channels,
        }
