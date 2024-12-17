import json
from pathlib import Path


class CollectionJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Path):
            return str(o)

        return super().default(o)
