# coding:utf-8

from typing import Generator
import unittest
from unittest.mock import MagicMock

from xhtml.request import stream


class TestStreamResponse(unittest.TestCase):

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
        fake_response = MagicMock()
        fake_response.status_code = 200
        fake_response.raw.headers = {"Content-Type": "text/html"}
        fake_response.cookies = [self.cookie]
        fake_response.iter_content.return_value = ["unittest", "unittest"]
        self.stream = stream.StreamResponse(fake_response)

    def tearDown(self):
        pass

    def test_generator(self):
        self.assertIsInstance(self.stream.generator, Generator)
        for chunk in self.stream.generator:
            self.assertEqual(chunk, "unittest")


if __name__ == "__main__":
    unittest.main()
