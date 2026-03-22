import socket
import logging
import signal
import sys
from common.utils import Bet
from common.utils import store_bets
CLIENT = "Client"
NAME = "Name"
LASTNAME = "LastName"
DNI = "Dni"
BIRTHDATE="Birthdate"
NUMBER ="Number"
KEY=0
VALUE=1

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._loop = True
        signal.signal(signal.SIGTERM, self.__handle_shutdown)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        while self._loop:
            try:
                client_sock = self.__accept_new_connection()
                self.__handle_client_connection(client_sock)
            except OSError:
                self._loop = False

    def __handle_shutdown(self,signal_number, stack_frame):
        logging.info("closing loop")
        self._loop = False
        logging.info("closing socket")
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()



    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            # TODO: Modify the receive to avoid short-reads
            msg = client_sock.recv(1024).rstrip().decode('utf-8')
            addr = client_sock.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
            # TODO: Modify the send to avoid short-writes
            self.__process_msg(msg)
            client_sock.send("{}\n".format(msg).encode('utf-8'))
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            client_sock.close()

    def __process_msg(self,msg):
        client_data = {}
        client_info =msg.split('|')
        for data in client_info:
            key_value = data.split(':')
            client_data[key_value[KEY]] = key_value[VALUE]
        logging.info(f'action: mensaje procesado  | result: {client_data} | from: {client_info}')
        new_bet = Bet(client_data[CLIENT], client_data[NAME], client_data[LASTNAME], client_data[DNI], client_data[BIRTHDATE], client_data[NUMBER])
        store_bets([new_bet])
        logging.info(f'action: apuesta_almacenada  | result: success | dni: {client_data[DNI]} | numero: {client_data[NUMBER]}')
        return 

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        try:
            c, addr = self._server_socket.accept()
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
            return c
        except OSError:
            raise OSError
        
        
