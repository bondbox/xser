# coding:utf-8

from socket import SOL_SOCKET
from socket import SO_RCVBUF  # noqa:H306
from socket import SO_SNDBUF
from socket import create_connection  # noqa:H306
from socket import socket
from socket import timeout
from threading import Thread
from time import sleep
from typing import Tuple

from xkits_lib import TimeUnit


class ResponseProxy():
    """Socket Response Proxy"""

    def __init__(self, client: socket, server: socket, chunk: int):
        self.__thread: Thread = Thread(target=self.handler)
        self.__client: socket = client
        self.__server: socket = server
        self.__running: bool = False
        self.__chunk: int = chunk

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
        seconds: float = 0.001

        try:
            while self.running:
                data: bytes = self.server.recv(self.chunk)
                if len(data) > 0:
                    seconds = max(0.001, seconds * 0.6)
                    self.client.sendall(data)
                else:
                    seconds = min(seconds * 1.1, 0.1)
                    sleep(seconds)
        except Exception:
            pass
        finally:
            self.server.close()
            self.client.close()

    def start(self):
        self.__running = True
        self.__thread.start()

    def stop(self):
        self.__running = False
        self.__thread.join()


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

    def new_connection(self, client: socket, data: bytes):
        server: socket = create_connection(address=self.target)
        server.setsockopt(SOL_SOCKET, SO_RCVBUF, self.chunk)
        server.setsockopt(SOL_SOCKET, SO_SNDBUF, self.chunk)
        client.setsockopt(SOL_SOCKET, SO_RCVBUF, self.chunk)
        client.setsockopt(SOL_SOCKET, SO_SNDBUF, self.chunk)
        client.settimeout(self.timeout)
        seconds: float = 0.001

        response: ResponseProxy = ResponseProxy(client, server, chunk=self.chunk)  # noqa:E501

        try:
            response.start()
            while True:
                if len(data) > 0:
                    seconds = max(0.001, seconds * 0.6)
                    server.sendall(data)
                else:
                    seconds = min(seconds * 1.1, 0.1)
                    sleep(seconds)
                data = client.recv(self.chunk)
        except timeout:
            pass
        except OSError:
            pass
        except Exception:
            pass
        finally:
            response.stop()
