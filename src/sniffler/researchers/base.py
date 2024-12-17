from datetime import datetime
from pathlib import Path
from typing import Protocol

InfoValue = str | int | float | None


class Researcher(Protocol):
    """
    Interface for a Researcher that defines methods to accept a file and retrieve information from it.
    """

    def accepts(self, file: Path) -> bool:
        """
        Determines if the given file is accepted.

        Args:
            file (Path): The file to be checked.

        Returns:
            bool: Always returns True.
        """
        ...

    def get_info(self, file: Path) -> dict[str, InfoValue]:
        """
        Retrieves information about a given file.

        Args:
            file (Path): The path to the file.

        Returns:
            dict[str, InfoValue]: A dictionary containing the file's stat information.
        """
        ...


class BasicResearcher:
    """
    BasicResearcher is a class that provides basic file research functionalities.
    """

    @staticmethod
    def accepts(file: Path) -> bool:
        return True

    def get_info(self, file: Path) -> dict[str, InfoValue]:
        stat = file.stat()

        def to_dt(timestamp: float | int) -> str:
            return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

        return {
            "name": file.name,
            "extension": file.suffix.lower(),
            "size": stat.st_size,
            "modified": to_dt(stat.st_mtime),
            "created": to_dt(stat.st_birthtime),
        }
