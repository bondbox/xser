# coding:utf-8

from typing import Iterable
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple


class Header():
    def __init__(self, headers: Optional[Iterable[Tuple[str, str]]] = None) -> None:  # noqa:E501
        self.__headers: List[Tuple[str, str]] = list(headers) if isinstance(headers, Iterable) else []  # noqa:E501

    def __len__(self) -> int:
        return len(self.__headers)

    def __iter__(self) -> Iterator[Tuple[str, str]]:
        return iter(self.__headers)

    def add(self, keyword: str, value: str) -> None:
        self.__headers.append((keyword, value))
