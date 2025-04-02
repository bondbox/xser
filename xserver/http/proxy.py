# coding:utf-8

from http.server import BaseHTTPRequestHandler
from typing import Dict
from typing import MutableMapping
from typing import Optional
from urllib.parse import urljoin

from requests import Response
from requests import get  # noqa:H306
from requests import post


class ProxyError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class MethodNotAllowed(ProxyError):
    def __init__(self) -> None:
        super().__init__("Method Not Allowed")


class ResponseProxy():
    """API Response Proxy"""
    CHUNK_SIZE: int = 1048576  # 1MB

    EXCLUDED_HEADERS = [
        "connection",
        "content-encoding",
        "content-length",
        "transfer-encoding",
    ]

    def __init__(self, response: Response) -> None:
        self.__response: Response = response

    @property
    def response(self) -> Response:
        return self.__response

    @property
    def headers(self) -> Dict[str, str]:
        return {k: v for k, v in self.response.headers.items()
                if k.lower() not in self.EXCLUDED_HEADERS}

    @property
    def generator(self):
        for chunk in self.response.iter_content(chunk_size=self.CHUNK_SIZE):
            yield chunk


class RequestProxy():
    """API Request Proxy"""

    EXCLUDED_HEADERS = [
        "connection",
        "content-length",
        "host",
        "keep-alive",
        "proxy-authorization",
        "transfer-encoding",
        "via",
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
        return {k: v for k, v in headers.items() if k.lower() not in cls.EXCLUDED_HEADERS}  # noqa:E501

    def request(self, path: str, method: str, data: Optional[bytes] = None,
                headers: Optional[MutableMapping[str, str]] = None
                ) -> ResponseProxy:
        url: str = self.urljoin(path.lstrip("/"))
        if method == "GET":
            response = get(
                url=url,
                data=data,
                headers=headers,
                stream=True
            )
            return ResponseProxy(response)
        if method == "POST":
            response = post(
                url=url,
                data=data,
                headers=headers,
                stream=True
            )
            return ResponseProxy(response)
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
        self.send_response(rp.response.status_code)
        for header, value in rp.headers.items():
            self.send_header(header, value)
        self.end_headers()
        for chunk in rp.generator:
            self.wfile.write(chunk)
            self.wfile.flush()
        rp.response.close()

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
