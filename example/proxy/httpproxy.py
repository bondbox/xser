# coding:utf-8

from http.server import ThreadingHTTPServer

from xserver.http.proxy import HttpProxy
from xserver.http.proxy import RequestProxy


def run(host: str, port: int):
    listen_address = (host, port)
    request_proxy: RequestProxy = RequestProxy("https://example.com/")
    httpd = ThreadingHTTPServer(listen_address, lambda *args: HttpProxy(*args, request_proxy=request_proxy))  # noqa:E501
    print(f"Listening on {host}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run("0.0.0.0", 5000)
