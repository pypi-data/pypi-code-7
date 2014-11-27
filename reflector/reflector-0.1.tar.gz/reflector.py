#!/usr/bin/env python
import argparse
import select
import socket
import sys


def get_server_socket(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setblocking(0)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(10)
    return server_socket


def main():
    parser = argparse.ArgumentParser(description='TCP connection reflector')
    parser.add_argument('listen_port', type=int, help='Port to listen on')
    parser.add_argument('--return-port', type=int,
                        help='Port to connect back to (defaults to listen_port)')

    args = parser.parse_args()

    if args.return_port is None:
        args.return_port = args.listen_port

    server_socket = get_server_socket(args.listen_port)

    sockets = [server_socket]
    mirror_connections = {}

    while True:
        rfds, _wfds, _xfds = select.select(sockets, [], [], 1)
        for rfd in rfds:
            if server_socket == rfd:
                conn, addr = server_socket.accept()
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    s.connect((addr[0], args.return_port))
                except Exception:
                    conn.close()
                sockets.append(s)
                sockets.append(conn)
                mirror_connections[s] = conn
                mirror_connections[conn] = s
            else:
                buf = rfd.recv(4096)
                if len(buf) == 0:
                    mirror_conn = mirror_connections[rfd]
                    sockets.remove(rfd)
                    sockets.remove(mirror_conn)
                    mirror_conn.close()
                    rfd.close()
                    del mirror_connections[mirror_conn]
                    del mirror_connections[rfd]
                    continue
                mirror_connections[rfd].send(buf)

if __name__ == '__main__':
    main()
