# coding:utf-8

import unittest

from xserver.sock import header


class TestRequestHeader(unittest.TestCase):

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

    def test_parse(self):
        request = header.RequestHeader.parse(b"GET / HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n")  # noqa:501
        self.assertIsInstance(request, header.RequestHeader)
        assert isinstance(request, header.RequestHeader)

        self.assertEqual(request.request_line.protocol, "HTTP/1.1")
        self.assertEqual(request.request_line.method, "GET")
        self.assertEqual(request.request_line.target, "/")

        self.assertIsInstance(request.headers, header.Header)

        self.assertEqual(request.length, 35)


class TestResponseHeader(unittest.TestCase):

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

    def test_parse(self):
        response = header.ResponseHeader.parse(b"HTTP/1.1 200 OK\r\nLocation: http://example.com/users/123\r\n\r\n")  # noqa:501
        self.assertIsInstance(response, header.ResponseHeader)
        assert isinstance(response, header.ResponseHeader)

        self.assertEqual(response.status_line.protocol, "HTTP/1.1")
        self.assertEqual(response.status_line.status_code, 200)
        self.assertEqual(response.status_line.status_text, "OK")

        self.assertIsInstance(response.headers, header.Header)

        self.assertEqual(response.length, 59)


if __name__ == "__main__":
    unittest.main()
