# coding:utf-8

import unittest
from unittest import mock

from xserver.sock import proxy


class TestResponseProxy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.fake_client = mock.MagicMock()
        self.fake_server = mock.MagicMock()
        self.fake_thread = mock.MagicMock()
        with mock.patch.object(proxy, "socket") as mock_socket:
            mock_socket.side_effect = [self.fake_client, self.fake_server]
            with mock.patch.object(proxy, "Thread") as mock_thread:
                client = proxy.socket()
                server = proxy.socket()
                self.assertIs(client, self.fake_client)
                self.assertIs(server, self.fake_server)
                mock_thread.side_effect = [self.fake_thread]
                self.proxy = proxy.ResponseProxy(client, server)

    def tearDown(self):
        pass

    def test_handler(self):
        self.fake_client.sendall.side_effect = [Exception()]
        self.fake_server.recv.side_effect = [b"test"]
        self.assertIsNone(self.proxy.start())
        self.assertIsNone(self.proxy.handler())
        self.assertIsNone(self.proxy.stop())


class TestSockProxy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.host = "0.0.0.0"
        cls.port = 12345
        cls.timeout = 60

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.proxy = proxy.SockProxy(self.host, self.port, self.timeout)

    def tearDown(self):
        pass

    @mock.patch.object(proxy, "socket")
    @mock.patch.object(proxy, "create_connection")
    @mock.patch.object(proxy.ResponseProxy, "stop", mock.MagicMock())
    @mock.patch.object(proxy.ResponseProxy, "start", mock.MagicMock())
    def test_new_connection_timeout(self, mock_create_connection, mock_socket):
        fake_client = mock.MagicMock()
        fake_server = mock.MagicMock()
        mock_socket.side_effect = [fake_client]
        mock_create_connection.side_effect = [fake_server]
        client = proxy.socket()
        self.assertIs(client, fake_client)
        fake_client.recv.side_effect = [proxy.timeout()]
        self.assertIsNone(self.proxy.new_connection(client, b"test"))

    @mock.patch.object(proxy, "socket")
    @mock.patch.object(proxy, "create_connection")
    @mock.patch.object(proxy.ResponseProxy, "stop", mock.MagicMock())
    @mock.patch.object(proxy.ResponseProxy, "start", mock.MagicMock())
    def test_new_connection_OSError(self, mock_create_connection, mock_socket):
        fake_client = mock.MagicMock()
        fake_server = mock.MagicMock()
        mock_socket.side_effect = [fake_client]
        mock_create_connection.side_effect = [fake_server]
        client = proxy.socket()
        self.assertIs(client, fake_client)
        fake_client.recv.side_effect = [OSError()]
        self.assertIsNone(self.proxy.new_connection(client, b"test"))

    @mock.patch.object(proxy, "socket")
    @mock.patch.object(proxy, "create_connection")
    @mock.patch.object(proxy.ResponseProxy, "stop", mock.MagicMock())
    @mock.patch.object(proxy.ResponseProxy, "start", mock.MagicMock())
    def test_new_connection_Exception(self, mock_create_connection, mock_socket):  # noqa:501
        fake_client = mock.MagicMock()
        fake_server = mock.MagicMock()
        mock_socket.side_effect = [fake_client]
        mock_create_connection.side_effect = [fake_server]
        client = proxy.socket()
        self.assertIs(client, fake_client)
        fake_client.recv.side_effect = [Exception()]
        self.assertIsNone(self.proxy.new_connection(client, b"test"))


if __name__ == "__main__":
    unittest.main()
