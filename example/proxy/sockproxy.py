# coding:utf-8

import socket

from xserver.sock.proxy import SockProxy


def run(listen_host: str, listen_port: int, target_host: str, target_port: int):  # noqa:E501
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((listen_host, listen_port))
    server_socket.listen(5)

    print(f"Listening on {listen_host}:{listen_port}")

    while True:
        client_socket, _ = server_socket.accept()
        SockProxy.start(target_host, target_port, client_socket)


if __name__ == "__main__":
    run("0.0.0.0", 8000, "localhost", 9000)
