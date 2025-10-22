# coding:utf-8

from typing import Iterable
from typing import List
from typing import Optional

from xhtml.header.headers import RequestLine
from xhtml.header.headers import StatusLine
from xhtml.header.headers import HeaderMapping


class RequestHeader():
    def __init__(self, request_line: str, request_headers: Iterable[str], header_length: int):  # noqa:E501
        self.__request_line: RequestLine = RequestLine(request_line)
        self.__headers: HeaderMapping = HeaderMapping.parse(request_headers)
        self.__length: int = header_length

    @property
    def request_line(self) -> RequestLine:
        return self.__request_line

    @property
    def headers(self) -> HeaderMapping:
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
        self.__headers: HeaderMapping = HeaderMapping.parse(response_headers)
        self.__length: int = header_length

    @property
    def status_line(self) -> StatusLine:
        return self.__status_line

    @property
    def headers(self) -> HeaderMapping:
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
