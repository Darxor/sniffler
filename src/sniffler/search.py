import re
from collections import defaultdict

from .collector import Collection


class SearchEngine:
    def __init__(self, collection: Collection):
        """
        Initializes the search object with a given collection and builds an index.

        Args:
            collection (Collection): The collection of items to be indexed and searched.
        """
        self.collection = collection
        self.index = self._build_index()

    def _build_index(self) -> dict[str, set[int]]:
        """
        Builds an index from the collection where each word maps to a set of indices
        of items in the collection that contain that word.

        Returns:
            dict[str, set[int]]: A dictionary where keys are words and values are sets
            of indices of items in the collection that contain those words.
        """
        index = defaultdict(set)
        for idx, item in enumerate(self.collection):
            for value in item.values():
                words = re.findall(r"\w+", str(value).lower())
                for word in words:
                    index[word].add(idx)
        return index

    def search(self, query: str) -> Collection:
        """
        Searches for items in the collection that match the given query.

        Args:
            query (str): The search query string.

        Returns:
            Collection: A new Collection instance containing items that match the query.
        """
        query = query.lower()
        matched_indices = set()
        for idx, item in enumerate(self.collection):
            if any(query in str(value).lower() for value in item.values()):
                matched_indices.add(idx)
        return Collection(self.collection[idx] for idx in matched_indices)
