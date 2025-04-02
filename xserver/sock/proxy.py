# coding:utf-8

from socket import create_connection
from socket import socket
from typing import Optional

from xkits_thread.executor import ThreadPool

from xserver.http.request import RequestHeader


class SockProxy():
    CHUNK_SIZE: int = 1048576  # 1MB

    def __init__(self, server_socket: socket, client_socket: socket):
        self.__server_socket: socket = server_socket
        self.__client_socket: socket = client_socket

    @property
    def server_socket(self) -> socket:
        return self.__server_socket

    @property
    def client_socket(self) -> socket:
        return self.__client_socket

    def server_handler(self):
        """receive data from server and send to client"""
        data: bytes = self.server_socket.recv(RequestHeader.MAX_HEADER)
        head: Optional[RequestHeader] = RequestHeader.parse(data)
        print(f"head: {head}")
        if isinstance(head, RequestHeader):
            dlen: int = head.request_length + head.content_length
            print(f"send {dlen} bytes to client")
            self.server_socket.sendall(data)
            dlen -= len(data)
            while (data := self.server_socket.recv(min(1048576, dlen))):
                # print(data)
                print(f"send {len(data)} to client")
                self.client_socket.sendall(data)
                dlen -= len(data)
            print("send to client end")

    def client_handler(self):
        """receive data from client and send to server"""
        data: bytes = self.client_socket.recv(RequestHeader.MAX_HEADER)
        head: Optional[RequestHeader] = RequestHeader.parse(data)
        if isinstance(head, RequestHeader):
            dlen: int = head.request_length + head.content_length
            print(f"send {dlen} bytes to server")
            self.server_socket.sendall(data)
            dlen -= len(data)
            while (data := self.client_socket.recv(min(1048576, dlen))):
                self.server_socket.sendall(data)
                dlen -= len(data)
            print("send to server end")

    @classmethod
    def start(cls, target_host: str, target_port: int, client_socket: socket):
        server_socket = create_connection((target_host, target_port))
        instance = cls(server_socket, client_socket)
        with ThreadPool() as pool:
            print("socket run")
            pool.submit(instance.server_handler)
            pool.submit(instance.client_handler)
            pool.shutdown(wait=True)
            instance.server_socket.close()
            instance.client_socket.close()
            print("socket end")
