from pathlib import Path

from mutagen._file import File

from .base import InfoValue


class AudioResearcher:
    """
    A class to perform research operations on audio files.
    """

    def accepts(self, file: Path) -> bool:
        return file.suffix.lower() in {".mp3", ".flac", ".ogg", ".wav", ".m4a"}

    def get_info(self, file: Path) -> dict[str, InfoValue]:
        audio = File(file, easy=True)
        tags = audio.tags if audio else {}

        return {
            "title": ";".join(tags.get("title", [])),
            "artist": ";".join(tags.get("artist", [])),
            "composer": ";".join(tags.get("composer", [])),
            "album": ";".join(tags.get("album", [])),
            "genre": ";".join(tags.get("genre", [])),
            "date": ";".join(tags.get("date", [])),
            "discnumber": ";".join(tags.get("discnumber", [])),
            "duration": audio.info.length if audio else None,
            "bitrate": audio.info.bitrate if audio else None,
            "samplerate": audio.info.sample_rate if audio else None,
            "channels": audio.info.channels if audio else None,
        }
