import socket
import logging
import signal
import sys
from common.utils import Bet
from common.utils import store_bets
from common.comm_module import CommModule
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
        self.__comm_module = CommModule(port, listen_backlog)
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
                self.__accept_new_connection()
                self.__handle_client_connection()
            except OSError:
                self._loop = False

    def __handle_shutdown(self,signal_number, stack_frame):
        logging.info("closing loop")
        self._loop = False
        logging.info("closing socket")
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()



    def __handle_client_connection(self):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            msg, addr=self.__comm_module.recv()
            logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
            amount_processed =self.__process_msg(msg)
            logging.info(f'action: apuesta_recibida | result: success | cantidad: {amount_processed}')
            self.__comm_module.send("{}".format(msg))
        except OSError as e:
            logging.error("action: receive_message | result: fail | error: {e}")
        finally:
            self.__comm_module.close()

    def __process_msg(self,msg):
        client_data = {}
        clients=msg.split('\n')
        n= 0
        for client in clients:
            if client == "": continue
            client_info =client.split('|')
            for data in client_info:
                key_value = data.split(':')
                client_data[key_value[KEY]] = key_value[VALUE]
            new_bet = Bet(client_data[CLIENT], client_data[NAME], client_data[LASTNAME], client_data[DNI], client_data[BIRTHDATE], client_data[NUMBER])
            store_bets([new_bet])
            logging.info(f'action: apuesta_almacenada  | result: success | dni: {client_data[DNI]} | numero: {client_data[NUMBER]}')
            n+=1
        return n

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        try:
            addr = self.__comm_module.accept_connection()
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
            return
        except OSError:
            raise OSError
        
        
