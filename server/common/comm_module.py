import socket
import logging
import signal
import sys
import threading

HEADER_LEN =4
ENDIAN = "big"
ENCODING = "utf-8"
SOCKET_CLOSED_ERROR = "Socket closed"

class CommModule:
    def __init__(self, port, listen_backlog):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._sockets = {}
        self._lock=  threading.Lock()

    def accept_connection(self):
        socket, addr = self._server_socket.accept()
        with self._lock:
            self._sockets[addr] = socket
        return  addr
    def recv(self, addr):
        header=self._recv_data(HEADER_LEN, addr)
        msg_len = int.from_bytes(header, byteorder=ENDIAN)
        msg = self._recv_data(msg_len, addr).decode(ENCODING)
        return msg
   
    def send(self, msg, addr):
        msg_bytes = msg.encode(ENCODING)
        msg_len = (len(msg_bytes)).to_bytes(HEADER_LEN, byteorder=ENDIAN, signed=False)
        with self._lock:
            client_socket = self._sockets[addr]
        try:
            _send_data(msg_len, client_socket)
            _send_data(msg_bytes, client_socket)
        except ConnectionError:
            raise ConnectionError(SOCKET_CLOSED_ERROR)
        return
    def close(self, addr):
        with self._lock:
            self._sockets[addr].close()
    def close_all(self):
        for _,connection in self._sockets.items():
            connection.close()
    def _recv_data(self, data_len, addr):
        data = b''
        with self._lock:
            client_socket = self._sockets[addr]
        data = client_socket.recv(data_len)
        while len(data) < data_len:
            new_data = client_socket.recv(data_len-len(data))
            if not new_data:
                raise ConnectionError(SOCKET_CLOSED_ERROR)
            data += new_data
        return data
    
def _send_data(msg, socket):
    bytes_sent = 0
    while bytes_sent < len(msg):
        n = socket.send(msg[bytes_sent:])
        if n == 0:
            raise ConnectionError(SOCKET_CLOSED_ERROR)
        bytes_sent += n