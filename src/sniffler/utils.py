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
