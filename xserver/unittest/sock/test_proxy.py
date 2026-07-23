# coding:utf-8

from unittest import TestCase
from unittest import main
from unittest import mock

from xserver.sock import proxy


class TestResponseProxy(TestCase):

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
                self.proxy = proxy.ResponseProxy(client, server, 65536)
                self.assertFalse(self.proxy.running)

    def tearDown(self):
        pass

    def test_handler(self):
        self.fake_client.fileno.side_effect = [1]
        self.fake_server.fileno.side_effect = [2]
        self.fake_server.recv.side_effect = [proxy.timeout(), b""]
        with mock.patch.object(type(self.proxy), "running", new_callable=mock.PropertyMock, return_value=True):  # noqa:E501
            self.assertIsNone(self.proxy.handler())
            self.assertEqual(self.proxy.total_received_from_client, 0)
            self.assertEqual(self.proxy.total_received_from_server, 0)

    def test_handler_Exception(self):
        self.fake_client.fileno.side_effect = [1]
        self.fake_server.fileno.side_effect = [2]
        self.fake_client.sendall.side_effect = [None, Exception()]
        self.fake_server.recv.side_effect = [proxy.timeout(), b"unit", b"test"]
        with mock.patch.object(type(self.proxy), "running", new_callable=mock.PropertyMock, return_value=True):  # noqa:E501
            self.assertIsNone(self.proxy.handler())
            self.assertEqual(self.proxy.total_received_from_client, 0)
            self.assertEqual(self.proxy.total_received_from_server, 4)


class TestSockProxy(TestCase):

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
    def test_new_connection(self, mock_create_connection, mock_socket):
        fake_client = mock.MagicMock()
        fake_server = mock.MagicMock()
        mock_socket.side_effect = [fake_client]
        mock_create_connection.side_effect = [fake_server]
        self.assertIs(client := proxy.socket(), fake_client)
        self.assertEqual(self.proxy.new_connection(client, b""), (0, 0))

    @mock.patch.object(proxy, "socket")
    @mock.patch.object(proxy, "create_connection")
    def test_new_connection_OSError(self, mock_create_connection, mock_socket):
        fake_client = mock.MagicMock()
        fake_server = mock.MagicMock()
        mock_socket.side_effect = [fake_client]
        mock_create_connection.side_effect = [fake_server]
        self.assertIs(client := proxy.socket(), fake_client)
        fake_client.recv.side_effect = [proxy.timeout(), OSError()]
        self.assertEqual(self.proxy.new_connection(client, b"test"), (4, 0))

    @mock.patch.object(proxy, "socket")
    @mock.patch.object(proxy, "create_connection")
    def test_new_connection_Exception(self, mock_create_connection, mock_socket):  # noqa:E501
        fake_client = mock.MagicMock()
        fake_server = mock.MagicMock()
        mock_socket.side_effect = [fake_client]
        mock_create_connection.side_effect = [fake_server]
        self.assertIs(client := proxy.socket(), fake_client)
        fake_client.recv.side_effect = [b"test", Exception()]
        self.assertEqual(self.proxy.new_connection(client, b"test"), (8, 0))


if __name__ == "__main__":
    main()
