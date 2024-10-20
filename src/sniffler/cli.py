import argparse
from functools import partial
from pathlib import Path

from tqdm import tqdm

from .collector import Collector
from .researcher import BasicResearcher, ImageResearcher

parser = argparse.ArgumentParser(description="Collect information about files in a directory.")
parser.add_argument(
    "path", type=Path, help="The path to the directory to collect information from.", nargs=1, default="."
)
parser.add_argument("-O", "--output", type=Path, help="The path to the output file.")


def main():
    args = parser.parse_args()

    researchers = [
        BasicResearcher(),
        ImageResearcher(),
    ]
    collector = Collector(args.path[0], researchers, progress_bar=partial(tqdm, desc="Collecting", unit=" files"))
    collector.collect(show_progress=bool(args.output))

    if args.output:
        with open(args.output, "w") as f:
            f.write(collector.collection.to_csv())
    else:
        print(collector.collection.to_csv())
