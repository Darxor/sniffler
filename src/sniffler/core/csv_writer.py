import contextlib
import csv
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any


def writer(f: Path | str | None):
    @contextlib.contextmanager
    def stdout():
        yield sys.stdout

    return open(f, "w") if f else stdout()


def localize_floats(row: Mapping[str, Any]) -> dict[str, Any]:
    """
    Converts all float values in the given dictionary to strings with commas as decimal separators.

    Args:
        row (Mapping[str, Any]): A dictionary where some values may be floats.

    Returns:
        dict[str, Any]: A new dictionary with float values converted to strings with commas as decimal separators.
    """
    return {
        key: str(value).replace(".", ",") if isinstance(value, float) else value
        for key, value in row.items()
    }


def write_csv(
    filename: Path | str | None,
    fieldnames: Iterable[str],
    data: Iterable[Mapping[str, Any]],
    delimiter: str = ",",
) -> None:
    """
    Write data to a CSV file with specified fieldnames and delimiter.

    Parameters:
        filename (Path | str | None): The path to the file where the CSV data will be written. If None, the output will be written to stdout.
        fieldnames (Iterable[str]): A list of field names for the CSV header.
        data (Iterable[Mapping[str, Any]]): An iterable of dictionaries containing the data to be written to the CSV file.
        delimiter (str, optional): The delimiter to use in the CSV file. Defaults to ",". When set to ";", the decimal separator will be a comma.

    Returns:
        None
    """
    if delimiter == "tab":
        delimiter = "\t"
    use_decimal_comma = delimiter == ";"
    with writer(filename) as f:
        w = csv.DictWriter(f, fieldnames=list(fieldnames), delimiter=delimiter)
        w.writeheader()
        if use_decimal_comma:
            for row in data:
                w.writerow(localize_floats(row))
        else:
            w.writerows(data)
