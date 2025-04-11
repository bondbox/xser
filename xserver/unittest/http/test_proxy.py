# coding:utf-8

from http.server import ThreadingHTTPServer
from threading import Thread
from time import sleep
import unittest
from unittest import mock

from requests.exceptions import ConnectionError

from xserver.http import proxy


class FakeProxy():
    def __init__(self, host: str, port: int):
        self.target_url = "https://example.com/"
        self.listen_address = (host, port)

    def run(self):
        self.httpd = ThreadingHTTPServer(
            self.listen_address, lambda *args: proxy.HttpProxy(
                *args, create_request_proxy=proxy.RequestProxy.create,
                target_url=self.target_url))
        self.httpd.serve_forever()


class TestResponseProxy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_generator(self):
        response = proxy.ResponseProxy.make_ok_response(b"test")
        self.assertEqual(response.status_code, 200)
        for chunk in response.generator:
            self.assertEqual(chunk, b"test")

    def test_close(self):
        self.assertIsNone(proxy.ResponseProxy(status_code=304, headers=proxy.Header()).close())  # noqa:E501

    def test_set_cookie(self):
        self.assertIsNone(proxy.ResponseProxy(status_code=404, headers=proxy.Header()).set_cookie("test", "unit"))  # noqa:E501

    def test_redirect(self):
        response = proxy.ResponseProxy.redirect()
        self.assertEqual(response.status_code, 302)
        for header in response.headers:
            self.assertEqual(header, ("Location", "/"))


class TestRequestProxyResponse(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.fake_response = mock.MagicMock()
        self.fake_response.status_code = 404
        self.fake_response.headers = {"Content-Length": "0"}
        self.fake_response.iter_content.side_effect = [["test"]]
        self.response = proxy.RequestProxyResponse(self.fake_response)

    def tearDown(self):
        pass

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 404)

    def test_headers(self):
        self.assertEqual(len(self.response.headers), 0)

    def test_generator(self):
        for chunk in self.response.generator:
            self.assertEqual(chunk, "test")

    def test_close(self):
        self.assertIsNone(self.response.close())


class TestRequestProxy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with mock.patch.object(proxy, "Session") as mock_session:
            cls.fake_session = mock.MagicMock()
            mock_session.side_effect = [cls.fake_session]
            cls.request_proxy: proxy.RequestProxy = proxy.RequestProxy("https://example.com/")  # noqa:E501

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_request_GET(self):
        self.assertIsInstance(self.request_proxy.request("test", "GET"), proxy.ResponseProxy)  # noqa:E501

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

    @mock.patch.object(proxy.RequestProxy, "request")
    @mock.patch.object(proxy.HttpProxy, "send_response")
    def test_forward_BrokenPipeError(self, mock_send_response, mock_request):
        mock_send_response.side_effect = [BrokenPipeError()]
        mock_request.side_effect = [self.fake_response]
        self.assertRaises(ConnectionError, proxy.Session().get, self.url)

    @mock.patch.object(proxy.RequestProxy, "request")
    def test_do_GET(self, mock_request):
        mock_request.side_effect = [self.fake_response]
        proxy.Session().get(self.url)

    @mock.patch.object(proxy.RequestProxy, "request")
    def test_do_POST(self, mock_request):
        mock_request.side_effect = [self.fake_response]
        proxy.Session().post(self.url)


if __name__ == "__main__":
    unittest.main()
