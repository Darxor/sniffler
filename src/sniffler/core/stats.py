from collections import Counter

from .collector import Collection


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
        cnt = Counter(
            str(file.get("extension", "no_extension")) for file in self.collection
        )
        cnt["no_extension"] += cnt.pop("")
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
