import math
from collections.abc import Callable
from functools import update_wrapper
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")


def inherit_signature_from(original: Callable[P, T]) -> Callable[[Callable], Callable[P, T]]:
    """Set the signature of one function to the signature of another."""

    def wrapper(f: Callable) -> Callable[P, T]:
        return update_wrapper(f, original)

    return wrapper


def convert_size(size_bytes: int | float) -> str:
    """
    Convert a file size in bytes to a human-readable string with appropriate units.

    Args:
        size_bytes (int | float): The size in bytes to be converted.

    Returns:
        str: The human-readable string representation of the file size.

    Examples:
        >>> convert_size(1024)
        '1.0 KB'
        >>> convert_size(1048576)
        '1.0 MB'
    """
    # https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"
