# coding:utf-8

from io import BytesIO
from typing import Dict
from typing import List
from typing import Optional


class RequestHandler:
    CHUNK_SIZE: int = 1048576  # 1MB

    def __init__(self):
        self.__buffer: BytesIO = BytesIO()

    def buffer(self) -> BytesIO:
        return self.__buffer


class RequestHeader():
    MAX_HEADER: int = 1048576  # 1MB

    def __init__(self, data: bytes):
        lines: List[str] = data.decode().split("\r\n")
        words: List[str] = lines[0].split()
        self.__headers: Dict[str, str] = {
            k: v for k, v in [line.split(": ") for line in lines[1:]]
        }
        self.__length: int = len(data) + 4
        self.__method: str = words[0]
        self.__path: str = words[1]

    @property
    def request_length(self) -> int:
        return self.__length

    @property
    def content_length(self) -> int:
        return int(self.headers.get("Content-Length", 0))

    @property
    def headers(self) -> Dict[str, str]:
        return self.__headers

    @property
    def method(self) -> str:
        return self.__method

    @property
    def path(self) -> str:
        return self.__path

    @classmethod
    def parse(cls, data: bytes) -> Optional["RequestHeader"]:
        offset: int = data.find(b"\r\n\r\n")
        return cls(data[:offset]) if offset > 0 else None
