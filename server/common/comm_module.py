import socket
import logging
import signal
import sys

HEADER_LEN =4

class CommModule:
    def __init__(self, port, listen_backlog):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._sockets = {}

    def accept_connection(self):
        socket, addr = self._server_socket.accept()
        self._sockets[addr] = socket
        return  addr
    def recv(self, addr):
        header=self._recv_data(HEADER_LEN, addr)
        msg_len = int.from_bytes(header, byteorder='big')
        msg = self._recv_data(msg_len, addr).decode('utf-8')
        return msg
   
    def send(self, msg, addr):
        msg_bytes = msg.encode('utf-8')
        msg_len = (len(msg_bytes)).to_bytes(HEADER_LEN, byteorder='big', signed=False)
        try:
            _send_data(msg_len, self._sockets[addr])
            _send_data(msg_bytes,  self._sockets[addr])
        except ConnectionError:
            raise ConnectionError("Socket closed")
        return
    def close(self, addr):
        self._sockets[addr].close()
    def close_all(self):
        for _,connection in self._sockets.items():
            connection.close()
    def _recv_data(self, data_len, addr):
        data = b''
        data = self._sockets[addr].recv(data_len)
        while len(data) < data_len:
            new_data = self._sockets[addr].recv(data_len-len(data))
            if not new_data:
                raise ConnectionError("Socket closed")
            data += new_data
        return data
    
def _send_data(msg, socket):
    bytes_sent = 0
    while bytes_sent < len(msg):
        n = socket.send(msg[bytes_sent:])
        if n == 0:
            raise ConnectionError("Socket closed")
        bytes_sent += n