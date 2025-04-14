# coding:utf-8

from socket import AF_INET
from socket import SOCK_STREAM
from socket import socket

from xkits_thread import ThreadPool

from xserver.sock.header import RequestHeader
from xserver.sock.proxy import SockProxy

CHUNK_SIZE: int = 1048576  # 1MB


def new_connection(proxy: SockProxy, client: socket):
    print(f"Connection {client.getpeername()} connecting")
    data: bytes = client.recv(CHUNK_SIZE)
    head = RequestHeader.parse(data)
    if head is not None:
        print(f"{head.request_line.method} {head.request_line.target}")
        proxy.new_connection(client, data)
    else:
        print(f"Invalid request: {data}")
        client.close()


def run(host: str, port: int):

    with socket(AF_INET, SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen(50)

        print(f"Server listening on {host}:{port}")
        with ThreadPool(max_workers=100) as pool:
            proxy: SockProxy = SockProxy("example.com", 80, 30)

            while True:
                client, _ = server.accept()
                pool.submit(new_connection, proxy, client)


if __name__ == "__main__":
    run("0.0.0.0", 8000)
