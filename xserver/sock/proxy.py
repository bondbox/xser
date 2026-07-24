# coding:utf-8

from socket import SHUT_RD
from socket import SHUT_WR
from socket import SOL_SOCKET
from socket import SO_RCVBUF  # noqa:H306
from socket import SO_SNDBUF
from socket import create_connection  # noqa:H306
from socket import socket
from socket import timeout
from threading import Thread
from typing import Tuple
from typing import Optional

from xkits_lib.unit import TimeUnit


class ResponseProxy():
    """Socket Response Proxy"""

    def __init__(self, client: socket, server: socket, chunk: int):
        self.__thread: Thread = Thread(target=self.handler)
        self.__except: Optional[Exception] = None
        self.__client: socket = client
        self.__server: socket = server
        self.__running: bool = False
        self.__sent_to_cli: int = 0
        self.__sent_to_srv: int = 0
        self.__chunk: int = chunk

    @property
    def total_received_from_client(self) -> int:
        return self.__sent_to_srv

    @property
    def total_received_from_server(self) -> int:
        return self.__sent_to_cli

    @property
    def client(self) -> socket:
        return self.__client

    @property
    def server(self) -> socket:
        return self.__server

    @property
    def running(self) -> bool:
        return self.__running

    @property
    def chunk(self) -> int:
        return self.__chunk

    def handler(self):
        try:
            while True:
                try:
                    data: bytes = self.server.recv(self.chunk)
                except timeout:
                    continue

                if (cnt := len(data)) == 0:
                    break

                self.client.sendall(data)
                self.__sent_to_cli += cnt
        except Exception as ex:
            self.__except = ex
        finally:
            self.close_socket(self.server, SHUT_RD)
            self.close_socket(self.client, SHUT_WR)
            self.__running = False

    def start(self, initial_data: bytes = b"", stop_threshold: int = 0) -> bool:  # noqa:E501
        try:
            self.__running = True
            self.__thread.start()

            if (cnt := len(initial_data)) > 0:
                self.server.sendall(initial_data)
                self.__sent_to_srv += cnt

            while True:
                if stop_threshold > 0 and self.__sent_to_srv >= stop_threshold:
                    break

                try:
                    data: bytes = self.client.recv(self.chunk)
                except timeout:
                    continue

                if (cnt := len(data)) == 0:
                    break

                self.server.sendall(data)
                self.__sent_to_srv += cnt
        except OSError as ex:
            self.__except = ex
        except Exception as ex:
            self.__except = ex
        finally:
            self.shutdown_socket(self.client, SHUT_RD)
            self.shutdown_socket(self.server, SHUT_WR)
            self.__thread.join()

        return not isinstance(self.__except, Exception)

    @classmethod
    def shutdown_socket(cls, sock: socket, how: int) -> bool:
        try:
            if sock.fileno() >= 0:
                sock.shutdown(how)
            return True
        except OSError:
            return False

    @classmethod
    def close_socket(cls, sock: socket, how: Optional[int] = None) -> bool:
        try:
            if sock.fileno() >= 0:
                if isinstance(how, int):
                    sock.shutdown(how)
                sock.close()
            return True
        except OSError:
            return False


class SockProxy():
    def __init__(self, host: str, port: int, timeout: TimeUnit, chunk: int = 65536):  # noqa:E501
        self.__target: Tuple[str, int] = (host, port)
        self.__timeout: TimeUnit = timeout
        self.__chunk: int = chunk

    @property
    def target(self) -> Tuple[str, int]:
        return self.__target

    @property
    def timeout(self) -> TimeUnit:
        return self.__timeout

    @property
    def chunk(self) -> int:
        return self.__chunk

    def new_connection(self, client: socket, initial_data: bytes, stop_threshold: int = 0) -> Tuple[int, int]:  # noqa:E501
        server: socket = create_connection(address=self.target)
        server.setsockopt(SOL_SOCKET, SO_RCVBUF, self.chunk)
        server.setsockopt(SOL_SOCKET, SO_SNDBUF, self.chunk)
        client.setsockopt(SOL_SOCKET, SO_RCVBUF, self.chunk)
        client.setsockopt(SOL_SOCKET, SO_SNDBUF, self.chunk)
        server.settimeout(self.timeout)
        client.settimeout(self.timeout)

        proxy: ResponseProxy = ResponseProxy(client, server, chunk=self.chunk)
        proxy.start(initial_data=initial_data, stop_threshold=stop_threshold)

        return (proxy.total_received_from_client, proxy.total_received_from_server)  # noqa:E501
