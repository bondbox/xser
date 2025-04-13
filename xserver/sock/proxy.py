# coding:utf-8

from socket import create_connection
from socket import socket
from socket import timeout
from threading import Thread
from typing import Tuple

from xkits_lib import TimeUnit

CHUNK_SIZE: int = 1048576  # 1MB


class ResponseProxy():
    """Socket Response Proxy"""

    def __init__(self, client: socket, server: socket) -> None:
        self.__thread: Thread = Thread(target=self.handler)
        self.__client: socket = client
        self.__server: socket = server
        self.__running: bool = False

    @property
    def client(self) -> socket:
        return self.__client

    @property
    def server(self) -> socket:
        return self.__server

    @property
    def running(self) -> bool:
        return self.__running

    def handler(self):
        try:
            while self.running:
                data: bytes = self.server.recv(CHUNK_SIZE)
                if len(data) > 0:
                    self.client.sendall(data)
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
    def __init__(self, host: str, port: int, timeout: TimeUnit):
        self.__target: Tuple[str, int] = (host, port)
        self.__timeout: TimeUnit = timeout

    @property
    def target(self) -> Tuple[str, int]:
        return self.__target

    @property
    def timeout(self) -> TimeUnit:
        return self.__timeout

    def new_connection(self, client: socket, data: bytes):
        client.settimeout(self.timeout)
        server: socket = create_connection(address=self.target)
        response: ResponseProxy = ResponseProxy(client, server)
        try:
            response.start()
            while True:
                if len(data) > 0:
                    server.sendall(data)
                data = client.recv(CHUNK_SIZE)
        except timeout:
            pass
        except OSError:
            pass
        except Exception:
            pass
        finally:
            response.stop()
