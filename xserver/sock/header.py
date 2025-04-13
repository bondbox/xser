# coding:utf-8

from typing import Dict
from typing import Iterable
from typing import List
from typing import Optional

from xhtml.header.headers import RequestLine
from xhtml.header.headers import StatusLine


class Header(Dict[str, str]):
    def __init__(self, headers: Iterable[str]) -> None:
        super().__init__()

        for header in headers:
            k, v = header.split(":", maxsplit=1)
            self.setdefault(k.strip(), v.strip())


class RequestHeader():
    def __init__(self, request_line: str, request_headers: Iterable[str], header_length: int):  # noqa:E501
        self.__request_line: RequestLine = RequestLine(request_line)
        self.__headers: Header = Header(request_headers)
        self.__length: int = header_length

    @property
    def request_line(self) -> RequestLine:
        return self.__request_line

    @property
    def headers(self) -> Header:
        return self.__headers

    @property
    def length(self) -> int:
        return self.__length

    @classmethod
    def parse(cls, data: bytes) -> Optional["RequestHeader"]:
        offset: int = data.find(b"\r\n\r\n")
        if offset > 0:
            content: str = data[:offset].decode("utf-8")
            headers: List[str] = content.split("\r\n")
            return cls(headers[0], headers[1:], offset + 4)


class ResponseHeader():
    def __init__(self, status_line: str, response_headers: Iterable[str], header_length: int):  # noqa:E501
        self.__status_line: StatusLine = StatusLine(status_line)
        self.__headers: Header = Header(response_headers)
        self.__length: int = header_length

    @property
    def status_line(self) -> StatusLine:
        return self.__status_line

    @property
    def headers(self) -> Header:
        return self.__headers

    @property
    def length(self) -> int:
        return self.__length

    @classmethod
    def parse(cls, data: bytes) -> Optional["ResponseHeader"]:
        offset: int = data.find(b"\r\n\r\n")
        if offset > 0:
            content: str = data[:offset].decode("utf-8")
            headers: List[str] = content.split("\r\n")
            return cls(headers[0], headers[1:], offset + 4)
