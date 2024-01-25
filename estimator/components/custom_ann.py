from annoy import AnnoyIndex
from typing import Literal
import json


class CustomAnnoy(AnnoyIndex):
    """
    Inherits AnnoyIndex: The save and load functions have been modified according to the website needs. This is the same ANN we used in
    search-engine-training-endpoint. Only modification to the real ANN class written by Spotify is our load functions. We are basically saying
    load our embeddings and labels as well
    """
    def __init__(self, f: int, metric: Literal["angular", "euclidean", "manhattan", "hamming", "dot"]):
        super().__init__(f, metric)
        self.label = []

    # noinspection PyMethodOverriding
    def add_item(self, i: int, vector, label: str) -> None:
        super().add_item(i, vector)
        self.label.append(label)

    def get_nns_by_vector(self, vector, n: int, search_k: int = ..., include_distances: Literal[False] = ...):
        indexes = super().get_nns_by_vector(vector, n)
        labels = [self.label[link] for link in indexes]
        return labels

    def load(self, fn: str, prefault: bool = ...):
        """
        Responsible for loading .ann and .json files saved by save method. This was the only modification made to the original ANN class
        written by spotify
        """
        super().load(fn)
        path = fn.replace(".ann", ".json")
        self.label = json.load(open(path, "r"))

    def save(self, fn: str, prefault: bool = ...):
        """
        Responsible for Saving .ann and .json files.
        """
        super().save(fn)
        path = fn.replace(".ann", ".json")
        json.dump(self.label, open(path, "w"))
