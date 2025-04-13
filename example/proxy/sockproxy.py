# coding:utf-8

from socket import AF_INET
from socket import SOCK_STREAM
from socket import socket

from xkits import ThreadPool

from xserver.sock.proxy import SockProxy


def run(host: str, port: int):

    with socket(AF_INET, SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen(50)

        print(f"Server listening on {host}:{port}")
        with ThreadPool(max_workers=100) as pool:
            proxy: SockProxy = SockProxy("example.com", 80, 30)

            while True:
                client, address = server.accept()
                print(f"Connection {address} connecting")
                pool.submit(proxy.new_connection, client)


if __name__ == "__main__":
    run("0.0.0.0", 8000)
