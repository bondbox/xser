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
        """server -> client"""
        try:
            while self.running:
                try:
                    data = self.server.recv(self.chunk)
                except timeout:
                    if not self.running:
                        break
                    continue

                if (cnt := len(data)) == 0:
                    break

                self.client.sendall(data)
                self.__sent_to_cli += cnt

            self.server_drained.set()
            self.client_drained.wait(timeout=5)
        except Exception as e:
            self.exception = e
        finally:
            self.close_socket(self.server, SHUT_WR)  # 关闭写端，通知对端
            self.close_socket(self.client, SHUT_RD)  # 关闭读端

    def start(self, initial_data: bytes = b"", stop_threshold: int = 0):
        """client -> server"""
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
                    if not self.running:
                        break
                    continue

                if (cnt := len(data)) == 0:
                    # client 关闭了连接
                    break

                self.server.sendall(data)
                self.__sent_to_srv += cnt

            self.shutdown_socket(self.client, SHUT_RD)
            if not self.server_drained.wait(timeout=10):
                # 超时处理，强制关闭
                print("Warning: server drain timeout")

            self.shutdown_socket(self.server, SHUT_WR)
            self.client_drained.set()
        except Exception as e:
            self.exception = e
        finally:
            self.__running = False
            # 等待 handler 线程结束
            if self.__thread and self.__thread.is_alive():
                self.__thread.join(timeout=5)

            # 最终清理
            self.close_socket(self.server)
            self.close_socket(self.client)

            # 检查异常
            if self.exception:
                raise self.exception

    @classmethod
    def shutdown_socket(cls, sock: socket, how: int):
        try:
            if sock.fileno() >= 0:
                sock.shutdown(how)
        except (OSError, ValueError):
            pass

    @classmethod
    def close_socket(cls, sock: socket, how: Optional[int] = None):
        try:
            if isinstance(how, int):
                if sock.fileno() >= 0:
                    sock.shutdown(how)
        except (OSError, ValueError):
            pass

        try:
            if sock.fileno() >= 0:
                sock.close()
        except (OSError, ValueError):
            pass


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
