import os
from collections.abc import Generator, Iterable
from pathlib import Path
from typing import Any, Protocol

from tqdm import tqdm

from .researcher import InfoValue, Researcher


class Explorer:
    def __init__(self, path: str | Path):
        self.path = Path(path).resolve(strict=True)

    def files(self) -> Generator[Path, Any, None]:
        for root, _, files in os.walk(self.path):
            for f in files:
                yield Path(root, f)


class Collection(list[dict[str, InfoValue]]):
    # use dict to ensure order of keys in Python 3.7+
    __keys = {}

    def append(self, object: dict[str, Any]) -> None:
        for k in object.keys():
            self.__keys[k] = None
        return super().append(object)

    def __repr__(self) -> str:
        return f"Collection({super().__repr__()})"

    def to_csv(self, sep: str = ",") -> str:
        keys = list(self.__keys.keys())
        lines = [keys]
        for item in self:
            lines.append([str(item.get(k, "")) for k in keys])
        return "\n".join(str(sep).join(line) for line in lines)

    def to_tsv(self) -> str:
        return self.to_csv(sep="\t")


class ProgressBar(Protocol):
    def __call__(self, iterable: Iterable, **kwargs: Any) -> Iterable: ...


class Collector:
    def __init__(self, path: str | Path, researchers: list[Researcher], progress_bar: ProgressBar = tqdm) -> None:
        self.path = Path(path).resolve(strict=True)
        self.explorer = Explorer(path)
        self.researchers = researchers
        self.collection: Collection = Collection()
        self.progress_bar = progress_bar

    def add_researcher(self, researcher: Researcher) -> None:
        self.researchers.append(researcher)

    def collect(self, show_progress: bool = False, progress_bar_kwargs: dict[str, Any] | None = None) -> None:
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
