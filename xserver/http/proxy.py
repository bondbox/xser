# coding:utf-8

from http.server import BaseHTTPRequestHandler
from typing import Any
from typing import Dict
from typing import Generator
from typing import List
from typing import MutableMapping
from typing import Optional
from typing import Tuple
from urllib.parse import urljoin

from requests import Response
from requests import get  # noqa:H306
from requests import post
from xhtml.header.headers import Headers


class ProxyError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class MethodNotAllowed(ProxyError):
    def __init__(self) -> None:
        super().__init__("Method Not Allowed")


class ResponseProxy():
    """API Response Proxy"""
    CHUNK_SIZE: int = 1048576  # 1MB

    def __init__(self, status_code: int, headers: List[Tuple[str, str]],
                 datas: bytes = b"") -> None:
        self.__status_code: int = status_code
        self.__headers: List[Tuple[str, str]] = headers
        self.__datas: bytes = datas

    @property
    def status_code(self) -> int:
        return self.__status_code

    @property
    def headers(self) -> List[Tuple[str, str]]:
        return self.__headers

    @property
    def generator(self) -> Generator[bytes, Any, None]:
        yield self.__datas

    def close(self):
        pass

    def set_cookie(self, keyword: str, value: str):
        self.headers.append((Headers.SET_COOKIE.value, f"{keyword}={value}"))

    @classmethod
    def make_ok_response(cls, datas: bytes) -> "ResponseProxy":
        headers: List[Tuple[str, str]] = [(Headers.CONTENT_LENGTH.value, str(len(datas)))]  # noqa:E501
        return ResponseProxy(status_code=200, headers=headers, datas=datas)

    @classmethod
    def redirect(cls, status_code: int = 302, location: str = "/") -> "ResponseProxy":  # noqa:E501
        headers: List[Tuple[str, str]] = [(Headers.LOCATION.value, location)]
        return ResponseProxy(status_code=status_code, headers=headers)


class RequestProxyResponse(ResponseProxy):
    """API Request Proxy Response"""

    EXCLUDED_HEADERS = [
        Headers.CONNECTION.value,
        Headers.CONTENT_ENCODING.value,
        Headers.CONTENT_LENGTH.value,
        Headers.TRANSFER_ENCODING.value,
    ]

    def __init__(self, response: Response) -> None:
        headers: List[Tuple[str, str]] = [i for i in response.headers.items() if i[0] not in self.EXCLUDED_HEADERS]  # noqa:E501
        super().__init__(status_code=response.status_code, headers=headers)
        self.__response: Response = response

    @property
    def generator(self):
        for chunk in self.__response.iter_content(chunk_size=self.CHUNK_SIZE):
            yield chunk

    def close(self):
        self.__response.close()


class RequestProxy():
    """API Request Proxy"""

    EXCLUDED_HEADERS = [
        Headers.CONNECTION.value,
        Headers.CONTENT_LENGTH.value,
        Headers.HOST.value,
        Headers.KEEP_ALIVE.value,
        Headers.PROXY_AUTHORIZATION.value,
        Headers.TRANSFER_ENCODING.value,
        Headers.VIA.value,
    ]

    def __init__(self, target_url: str) -> None:
        self.__target_url: str = target_url

    @property
    def target_url(self) -> str:
        return self.__target_url

    def urljoin(self, path: str) -> str:
        return urljoin(base=self.target_url, url=path)

    @classmethod
    def filter_headers(cls, headers: MutableMapping[str, str]) -> Dict[str, str]:  # noqa:E501
        return {k: v for k, v in headers.items() if k not in cls.EXCLUDED_HEADERS}  # noqa:E501

    def request(self, path: str, method: str, data: Optional[bytes] = None,
                headers: Optional[MutableMapping[str, str]] = None
                ) -> RequestProxyResponse:
        url: str = self.urljoin(path.lstrip("/"))
        if method == "GET":
            response = get(
                url=url,
                data=data,
                headers=headers,
                stream=True
            )
            return RequestProxyResponse(response)
        if method == "POST":
            response = post(
                url=url,
                data=data,
                headers=headers,
                stream=True
            )
            return RequestProxyResponse(response)
        raise MethodNotAllowed()


class HttpProxy(BaseHTTPRequestHandler):
    def __init__(self, *args, request_proxy: RequestProxy):
        self.__request_proxy: RequestProxy = request_proxy
        super().__init__(*args)

    @property
    def request_proxy(self) -> RequestProxy:
        return self.__request_proxy

    def get_request_data(self):
        content_length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(content_length) if content_length > 0 else None

    def forward(self, rp: ResponseProxy):
        self.send_response(rp.status_code)
        for header in rp.headers:
            k: str = header[0]
            v: str = header[1]
            self.send_header(k, v)
        self.end_headers()
        for chunk in rp.generator:
            self.wfile.write(chunk)
            self.wfile.flush()
        rp.close()

    def do_GET(self):
        headers = self.request_proxy.filter_headers(
            {k: v for k, v in self.headers.items()})
        response = self.request_proxy.request(
            path=self.path,
            method="GET",
            data=self.get_request_data(),
            headers=headers)
        self.forward(response)

    def do_POST(self):
        headers = self.request_proxy.filter_headers(
            {k: v for k, v in self.headers.items()})
        response = self.request_proxy.request(
            path=self.path,
            method="POST",
            data=self.get_request_data(),
            headers=headers)
        self.forward(response)
