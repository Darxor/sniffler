import argparse
from functools import partial
from pathlib import Path

from tqdm import tqdm

from .collector import Collector
from .csv_writer import write_csv
from .researcher import BasicResearcher, ImageResearcher

parser = argparse.ArgumentParser(description="Collect information about files in a directory.")
parser.add_argument(
    "path", type=Path, help="The path to the directory to collect information from.", nargs=1, default="."
)
parser.add_argument("-O", "--output", type=Path, help="The path to the output file.")
parser.add_argument("--delimiter", type=str, help="The delimiter to use in the output file (',', ';', or 'tab').", default=",")


def main():
    args = parser.parse_args()

    researchers = [
        BasicResearcher(),
        ImageResearcher(),
    ]
    collector = Collector(args.path[0], researchers, progress_bar=partial(tqdm, desc="Collecting", unit=" files"))
    collector.collect(show_progress=bool(args.output))

    write_csv(args.output, collector.collection.keys, collector.collection, delimiter=args.delimiter)
