# coding:utf-8

from http.server import ThreadingHTTPServer
from threading import Thread
from time import sleep
import unittest
from unittest import mock

from xserver.http import proxy
from xserver.http.proxy import HttpProxy
from xserver.http.proxy import RequestProxy


class FakeProxy():
    def __init__(self, host: str, port: int):
        self.request_proxy: RequestProxy = RequestProxy("https://example.com/")
        self.listen_address = (host, port)

    def run(self):
        self.httpd = ThreadingHTTPServer(self.listen_address, lambda *args: HttpProxy(*args, request_proxy=self.request_proxy))  # noqa:E501
        self.httpd.serve_forever()


class TestResponseProxy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.fake_response = mock.MagicMock()
        self.response = proxy.ResponseProxy(self.fake_response)

    def tearDown(self):
        pass

    def test_status_code(self):
        self.fake_response.status_code = 404
        self.assertEqual(self.response.status_code, 404)

    def test_headers(self):
        self.fake_response.headers = {"Content-Length": "0"}
        self.assertEqual(self.response.headers, {})

    def test_cookies(self):
        self.fake_response.cookies = ["test=unit"]
        self.assertEqual(self.response.cookies, ["test=unit"])

    def test_generator(self):
        self.fake_response.iter_content.side_effect = [["test"]]
        for chunk in self.response.generator:
            self.assertEqual(chunk, "test")

    def test_close(self):
        self.assertIsNone(self.response.close())


class TestRequestProxy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.request_proxy: RequestProxy = RequestProxy("https://example.com/")

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch.object(proxy, "get", mock.MagicMock())
    def test_request_GET(self):
        self.assertIsInstance(self.request_proxy.request("test", "GET"), proxy.ResponseProxy)  # noqa:E501

    @mock.patch.object(proxy, "post", mock.MagicMock())
    def test_request_POST(self):
        self.assertIsInstance(self.request_proxy.request("test", "POST"), proxy.ResponseProxy)  # noqa:E501

    def test_request_MethodNotAllowed(self):
        self.assertRaises(proxy.MethodNotAllowed, self.request_proxy.request, "test", "PUT")  # noqa:E501


class TestHttpProxy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.port = 12345
        cls.host = "localhost"
        cls.url = f"http://{cls.host}:{cls.port}/test"
        cls.fake_proxy = FakeProxy(cls.host, cls.port)
        cls.thread = Thread(target=cls.fake_proxy.run)
        cls.thread.start()
        fake_response = mock.MagicMock()
        fake_response.status_code = 200
        fake_response.headers = {
            "Accept-Ranges": "bytes",
            "Content-Type": "text/html",
            "ETag": '"84238dfc8092e5d9c0dac8ef93371a07:1736799080.121134"',
            "Last-Modified": "Mon, 13 Jan 2025 20:11:20 GMT",
            "Vary": "Accept-Encoding",
            "Cache-Control": "max-age=771",
            "Date": "Wed, 02 Apr 2025 15:49:17 GMT",
            "Alt-Svc": 'h3=":443"; ma=93600,h3-29=":443"; ma=93600,quic=":443"; ma=93600; v="43"',  # noqa:E501
        }
        fake_response.generator = [b'<!doctype html>\n<html>\n<head>\n    <title>Example Domain</title>\n\n    <meta charset="utf-8" />\n    <meta http-equiv="Content-type" content="text/html; charset=utf-8" />\n    <meta name="viewport" content="width=device-width, initial-scale=1" />\n    <style type="text/css">\n    body {\n        background-color: #f0f0f2;\n        margin: 0;\n        padding: 0;\n        font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", "Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;\n        \n    }\n    div {\n        width: 600px;\n        margin: 5em auto;\n        padding: 2em;\n        background-color: #fdfdff;\n        border-radius: 0.5em;\n        box-shadow: 2px 3px 7px 2px rgba(0,0,0,0.02);\n    }\n    a:link, a:visited {\n        color: #38488f;\n        text-decoration: none;\n    }\n    @media (max-width: 700px) {\n        div {\n            margin: 0 auto;\n            width: auto;\n        }\n    }\n    </style>    \n</head>\n\n<body>\n<div>\n    <h1>Example Domain</h1>\n    <p>This domain is for use in illustrative examples in documents. You may use this\n    domain in literature without prior coordination or asking for permission.</p>\n    <p><a href="https://www.iana.org/domains/example">More information...</a></p>\n</div>\n</body>\n</html>\n']  # noqa:E501
        cls.fake_response = fake_response
        sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        cls.fake_proxy.httpd.shutdown()

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_do_GET(self):
        with mock.patch.object(self.fake_proxy.request_proxy, "request") as mock_request:  # noqa:E501
            mock_request.side_effect = [self.fake_response]
            proxy.get(self.url)

    def test_do_POST(self):
        with mock.patch.object(self.fake_proxy.request_proxy, "request") as mock_request:  # noqa:E501
            mock_request.side_effect = [self.fake_response]
            proxy.post(self.url)


if __name__ == "__main__":
    unittest.main()
