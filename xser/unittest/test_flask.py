# coding:utf-8

import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

from flask import Request
from werkzeug.test import EnvironBuilder

from xhtml.flask import proxy


class TestFlaskProxy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cookie = MagicMock()
        cls.cookie.name = "test"
        cls.cookie.value = "unittest"
        cls.cookie.expires = 1000
        cls.cookie.path = "/"
        cls.cookie.domain = "example.com"
        cls.cookie.secure = True

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.proxy = proxy.FlaskProxy("http://example.com")

    def tearDown(self):
        pass

    @patch.object(proxy, "stream_with_context")
    def test_request_get_success(self, mock_stream_with_context):
        with patch.object(self.proxy.session, "get") as mock_get:
            fake_response = MagicMock()
            fake_response.status_code = 200
            fake_response.raw.headers = {"Content-Type": "text/html"}
            fake_response.cookies = [self.cookie]
            mock_get.return_value = fake_response
            mock_stream_with_context.side_effect = ["unittest"]
            request = Request(EnvironBuilder().get_environ())
            response = self.proxy.request(request)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers["Content-Type"], "text/html")

    @patch.object(proxy, "stream_with_context")
    def test_request_post_success(self, mock_stream_with_context):
        with patch.object(self.proxy.session, "post") as mock_post:
            fake_response = MagicMock()
            fake_response.status_code = 201
            fake_response.raw.headers = {"Content-Type": "application/json"}
            fake_response.cookies = [self.cookie]
            mock_post.return_value = fake_response
            mock_stream_with_context.side_effect = ["unittest"]
            request = Request(EnvironBuilder(method="post").get_environ())
            response = self.proxy.request(request)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.headers["Content-Type"], "application/json")  # noqa:E501

    def test_request_UnsupportedMethod(self):
        with patch.object(self.proxy.session, "get"):
            request = Request(EnvironBuilder(method="put").get_environ())
            response = self.proxy.request(request)
            self.assertEqual(response.status_code, 405)

    def test_request_ConnectionError(self):
        with patch.object(self.proxy.session, "get") as mock_get:
            mock_get.side_effect = proxy.ConnectionError
            request = Request(EnvironBuilder().get_environ())
            response = self.proxy.request(request)
            self.assertEqual(response.status_code, 502)


if __name__ == "__main__":
    unittest.main()
