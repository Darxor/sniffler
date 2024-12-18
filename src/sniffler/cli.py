import argparse
from functools import partial
from pathlib import Path

from tqdm import tqdm

from .core.collector import Collection, Collector
from .core.csv_writer import write_csv
from .core.search import SearchEngine
from .core.stats import StatCalculator
from .core.utils import convert_size
from .researchers import (
    AudioResearcher,
    BasicResearcher,
    ImageResearcher,
    LegacyOfficeResearcher,
    ModernOfficeResearcher,
    PdfResearcher,
)

parser = argparse.ArgumentParser(description="Collect information about files in a directory.")
parser.add_argument(
    "path",
    type=Path,
    help="The path to the directory to collect information from.",
    nargs=1,
    default=".",
)
parser.add_argument("-O", "--output", type=Path, help="The path to the output file.")
parser.add_argument(
    "--delimiter",
    type=str,
    help="The delimiter to use in the output file (',', ';', or 'tab').",
    default=",",
)
parser.add_argument(
    "--search",
    type=str,
    help="Search for files containing the given string in filename or attributes.",
    default=None,
)


def main():
    args = parser.parse_args()

    researchers = [
        BasicResearcher(),
        ImageResearcher(),
        AudioResearcher(),
        PdfResearcher(),
        ModernOfficeResearcher(),
        LegacyOfficeResearcher(),
    ]
    collector = Collector(
        args.path[0],
        researchers,
        progress_bar=partial(tqdm, desc="Collecting", unit=" files"),
    )
    collector.collect(show_progress=bool(args.output))
    stats_calculator = StatCalculator(collector.collection)

    search_results = Collection()
    if args.search:
        search_engine = SearchEngine(collector.collection)
        search_results = search_engine.search(args.search)

    if args.output:
        write_csv(
            args.output,
            collector.collection.keys,
            collector.collection,
            delimiter=args.delimiter,
        )
    else:
        print("Total files:", stats_calculator.total_files())
        print("Total file size:", convert_size(stats_calculator.total_size()))

        print("Count by extension:")
        for ext, count in stats_calculator.count_by_extension().most_common():
            print(f"\t{ext}: {count}")

        print("Top 10 largest files:")
        for file in stats_calculator.top_n_largest_files(10):
            print(f"\t{file['path']} ({convert_size(int(file['size']))})")  # type: ignore

        if search_results:
            print("\nSearch results:")
            for file in search_results:
                print(f"\t{file['path']}")
