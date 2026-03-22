import socket
import logging
import signal
import sys

class CommModule:
    def __init__(self, port, listen_backlog):
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.__client_socket:socket = None
    
    def accept_connection(self):
        self.__client_socket, ip = self._server_socket.accept()
        return  ip
    def recv(self):
        header=self._recv_data(4)
        msg_len = int.from_bytes(header, byteorder='big')
        msg = self._recv_data(msg_len).decode('utf-8')
        addr = self.__client_socket.getpeername()
        return msg, addr
    def send(self, msg):
        bytes_sent = 0
        msg_bytes = msg.encode('utf-8')
        while bytes_sent < len(msg):
            n = self.__client_socket.send(msg_bytes[bytes_sent:])
            if n == 0:
                raise ConnectionError("Socket closed")
            bytes_sent += n
    def close(self):
        self.__client_socket.close()
    def _recv_data(self, data_len):
        data = b''
        data = self.__client_socket.recv(data_len)
        while len(data) < data_len:
            new_data = self.__client_socket.recv(data_len-len(data))
            recived_amount += len(data)
            if not new_data:
                raise ConnectionError("Socket closed")
            data += new_data
        return data