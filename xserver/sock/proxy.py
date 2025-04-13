# coding:utf-8

from socket import create_connection
from socket import socket
from socket import timeout
from threading import Thread
from typing import Optional
from typing import Tuple


class ResponseProxy():
    """Socket Response Proxy"""
    CHUNK_SIZE: int = 1048576  # 1MB

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
                data: bytes = self.server.recv(self.CHUNK_SIZE)
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
    def __init__(self, host: str, port: int, timeout: float):
        self.__target: Tuple[str, int] = (host, port)
        self.__timeout: float = timeout

    @property
    def target(self) -> Tuple[str, int]:
        return self.__target

    @property
    def timeout(self) -> float:
        return self.__timeout

    def new_connection(self, client: socket):
        response: Optional[ResponseProxy] = None
        try:
            client.settimeout(self.timeout)
            server = create_connection(address=self.target)
            response = ResponseProxy(client, server)
            response.start()
            while True:
                data: bytes = client.recv(ResponseProxy.CHUNK_SIZE)
                if len(data) > 0:
                    server.sendall(data)
        except timeout:
            pass
        except OSError:
            pass
        except Exception:
            pass
        finally:
            if response is not None:
                response.stop()
