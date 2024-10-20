import os
from collections.abc import Generator, Iterable
from pathlib import Path
from typing import Any, Protocol

from tqdm import tqdm

from .researchers import InfoValue, Researcher


class Explorer:
    def __init__(self, path: str | Path):
        """
        Initializes the Collector with the given path.

        Args:
            path (str | Path): The file system path to be resolved.

        Raises:
            FileNotFoundError: If the path does not exist.
        """
        self.path = Path(path).resolve(strict=True)

    def files(self) -> Generator[Path, Any, None]:
        """
        Generates a sequence of file paths within the specified directory.

        Yields:
            Generator[Path, Any, None]: A generator that yields Path objects for each file found in the directory tree.
        """
        for root, _, files in os.walk(self.path):
            for f in files:
                yield Path(root, f)


class Collection(list[dict[str, InfoValue]]):
    """
    Collection is a custom list subclass that stores dictionaries with string keys and InfoValue values.
    It maintains the order of keys across all dictionaries added to it.
    """

    # use dict to ensure order of keys in Python 3.7+
    __keys = {}

    def append(self, object: dict[str, Any]) -> None:
        """
        Appends a dictionary object to the collection and updates the internal keys.

        Args:
            object (dict[str, Any]): The dictionary object to append.

        Returns:
            None
        """
        for k in object.keys():
            self.__keys[k] = None
        return super().append(object)

    def __repr__(self) -> str:
        return f"Collection({super().__repr__()})"

    @property
    def keys(self) -> list[str]:
        """
        Returns the keys in the collection.

        Returns:
            list[str]: A list of keys.
        """
        return list(self.__keys.keys())


class ProgressBar(Protocol):
    def __call__(self, iterable: Iterable, **kwargs: Any) -> Iterable: ...


class Collector:
    def __init__(self, path: str | Path, researchers: list[Researcher], progress_bar: ProgressBar = tqdm) -> None:
        """
        Initializes the Collector instance.

        Args:
            path (str | Path): The path to the directory to be explored.
            researchers (list[Researcher]): A list of Researcher instances.
            progress_bar (ProgressBar, optional): A progress bar instance, defaults to tqdm.

        Attributes:
            path (Path): The resolved absolute path to the directory.
            explorer (Explorer): An Explorer instance for the given path.
            researchers (list[Researcher]): A list of Researcher instances.
            collection (Collection): A Collection instance to store collected data.
            progress_bar (ProgressBar): A progress bar instance.
        """
        self.path = Path(path).resolve(strict=True)
        self.explorer = Explorer(path)
        self.researchers = researchers
        self.collection: Collection = Collection()
        self.progress_bar = progress_bar

    def add_researcher(self, researcher: Researcher) -> None:
        """
        Adds a researcher to the list of researchers.

        Args:
            researcher (Researcher): The researcher to be added.
        """
        self.researchers.append(researcher)

    def collect(self, show_progress: bool = False, progress_bar_kwargs: dict[str, Any] | None = None) -> None:
        """
        Collects information about files using the configured researchers and adds it to the collection.

        Args:
            show_progress (bool): If True, displays a progress bar during collection. Defaults to False.
            progress_bar_kwargs (dict[str, Any] | None): Additional keyword arguments to pass to the progress bar. Defaults to None.

        Returns:
            None
        """
        file_iterator = self.explorer.files()

        if progress_bar_kwargs is None:
            progress_bar_kwargs = {}

        if show_progress:
            file_iterator = self.progress_bar(file_iterator, **progress_bar_kwargs)

        for f in file_iterator:
            file_info = {"path": f.relative_to(self.path)}
            for researcher in self.researchers:
                if researcher.accepts(f):
                    file_info |= researcher.get_info(f)
            self.collection.append(file_info)
