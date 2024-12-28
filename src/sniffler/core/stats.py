from collections import Counter
from pathlib import Path

from .collector import Collection
from ..researchers import ImageResearcher, LegacyOfficeResearcher, ModernOfficeResearcher, PdfResearcher


class StatCalculator:
    def __init__(self, collection: Collection) -> None:
        """
        Initializes the Stats object with a given Collector instance.

        Args:
            collection (Collection): The collectoin instance used for gathering statistics.
        """
        self.collection = collection

    def total_files(self) -> int:
        """
        Calculate the total number of files collected.

        Returns:
            int: The total number of files in the collection.
        """
        return len(self.collection)

    def total_size(self) -> int:
        """
        Calculate the total size of all files in the collection.

        Returns:
            int: The total size of all files in the collection.
        """
        return sum(float(file.get("size", 0)) for file in self.collection)  # type: ignore

    def count_by_extension(self) -> Counter[str]:
        """
        Count the occurrences of each file extension in the collection.

        This method iterates over the files in the collector's collection and counts
        the number of times each file extension appears. Files without an extension
        are counted under the key "no_extension".

        Returns:
            Counter[str]: A Counter object where the keys are file extensions and the
                          values are the counts of files with those extensions.
        """
        cnt = Counter(str(file.get("extension", "no_extension")) for file in self.collection)
        try:
            cnt["no_extension"] += cnt.pop("")
        except KeyError:
            pass
        return cnt

    def top_n_largest_files(self, n: int) -> Collection:
        """
        Returns the top N largest files from the collection.

        Args:
            n (int): The number of largest files to return.

        Returns:
            Collection: A collection of the top N largest files, sorted by size in descending order.
        """
        return sorted(self.collection, key=lambda x: float(int(x.get("size", 0))), reverse=True)[:n]  # type: ignore

    def top_n_largest_images(self, n: int) -> Collection:
        """
        Returns the top N largest images from the collection.

        Args:
            n (int): The number of largest images to return.

        Returns:
            Collection: A collection of the top N largest images, sorted by size in descending order.
        """
        images = [file for file in self.collection if ImageResearcher().accepts(Path(str(file.get("path"))))]

        def get_area(file):
            return float(file.get("width", 0)) * float(file.get("height", 0))

        return Collection(sorted(images, key=get_area, reverse=True)[:n])

    def top_n_documents_by_pages(self, n: int) -> Collection:
        """
        Returns
        """

        def get_page_count(file):
            return int(file.get("page_count", 0))

        def get_path(file):
            path = file.get("path")
            if path:
                return Path(path)
            else:
                return Path("")

        documents = [
            file
            for file in self.collection
            if any(
                researcher.accepts(file=get_path(file))
                for researcher in (PdfResearcher, ModernOfficeResearcher, LegacyOfficeResearcher)
            )
        ]

        return Collection(sorted(documents, key=get_page_count, reverse=True)[:n])
