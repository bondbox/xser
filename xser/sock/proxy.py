# coding:utf-8

from socket import create_connection
from socket import socket

from xkits import ThreadPool


class SockProxy():
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
        while (data := self.server_socket.recv(1048576)):
            print(f"send {len(data)} to client")
            self.client_socket.sendall(data)
            # print(data)
        print("send to client end")
        self.server_socket.close()

    def client_handler(self):
        while (data := self.client_socket.recv(1048576)):
            print(f"send {len(data)} to server")
            self.server_socket.sendall(data)
            # print(data)
        print("send to server end")
        self.client_socket.close()

    @classmethod
    def start(cls, target_host: str, target_port: int, client_socket: socket):
        server_socket = create_connection((target_host, target_port))
        instance = cls(server_socket, client_socket)
        with ThreadPool() as pool:
            print("socket run")
            pool.submit(instance.server_handler)
            pool.submit(instance.client_handler)
            for thread in pool._threads:
                print(f"wait thread {thread}")
                thread.join()
            print("socket end")
