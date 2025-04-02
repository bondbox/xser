# coding:utf-8

from socket import socket


class SockStream():
    def __init__(self, sock: socket):
        self.__socket: socket = sock

    @property
    def sock(self) -> socket:
        return self.__socket
