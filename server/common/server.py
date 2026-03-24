import socket
import logging
import signal
import sys
from common.utils import Bet
from common.utils import store_bets
from common.utils import load_bets
from common.utils import has_won
from common.comm_module import CommModule
import threading
CLIENT = "Client"
NAME = "Name"
LASTNAME = "LastName"
DNI = "Dni"
BIRTHDATE="Birthdate"
NUMBER ="Number"
KEY=0
VALUE=1

PENDING = False
DONE = True
FINISHED_SENDING = "\n"


class Server:
    def __init__(self, port, listen_backlog, agency_amount):
        # Initialize server socket
        self.__comm_module = CommModule(port, listen_backlog)
        self._loop = True
        self._agency_addr = {}
        self._agency_status = {}
        self._agency_amount = agency_amount
        self._threads = []
        self._lock=  threading.Lock()
        signal.signal(signal.SIGTERM, self.__handle_shutdown)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        agencies_conected = 0
        while self._loop:
            if len(self._agency_status.keys()) == self._agency_amount:
                for thread in self._threads:
                    thread.join()
                logging.info('action: sorteo | result: success')
                self.process_bets()
                self._agency_status ={}
            else:
                try:
                    addr=self.__accept_new_connection()
                    thread=threading.Thread(target=self.__handle_client_connection, args=(addr,))
                    thread.start()
                    with self._lock:
                        self._threads.append(thread)
                except OSError:
                    self._loop = False
                    self.__comm_module.close_all()

    def _all_agencies_done(self):
        for agency_status in self._agency_status.values():
            if agency_status ==PENDING:
                return False
        return True

    def __handle_shutdown(self,signal_number, stack_frame):
        logging.info("closing loop")
        self._loop = False
        logging.info("closing socket")
        self._server_socket.shutdown(socket.SHUT_RDWR)
        self._server_socket.close()
        logging.info("joining dangling threads")
        for thread in self._threads:
            thread.join()

    def process_bets(self):
        bets=load_bets()
        agencies_winners = {agency_id: [] for agency_id in self._agency_addr.keys()}
        logging.info(f'ganador de agencia bets {bets}')
        for bet in bets:
            if has_won(bet):
                agencies_winners[bet.agency].append(bet.document)
        logging.info(f'ganador de agencia items {agencies_winners}')
        for agency,winners in agencies_winners.items():
            winners_message="|".join(winners)
            self.__comm_module.send(winners_message, self._agency_addr[agency])
        return

    def __handle_client_connection(self, addr):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        with self._lock:
            agency_status=self._agency_status[addr]
        try:
            while  agency_status == PENDING:
                msg=self.__comm_module.recv(addr)
                logging.info(f'action: receive_message | result: success | ip: {addr[0]} | msg: {msg}')
                if msg == FINISHED_SENDING:
                    with self._lock:
                        agency_status = DONE
                        self._agency_status[addr] = DONE
                else:
                    amount_processed =self.__process_msg(msg, addr)
                    logging.info(f'action: apuesta_recibida | result: success | cantidad: {amount_processed}')
                #self.__comm_module.send("{}".format(msg), addr)
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
            self.__comm_module.send("Error {}".format(500), addr)

    def __process_msg(self,msg, addr):
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
            with self._lock:
                store_bets([new_bet])
                logging.info(f'action: apuesta_almacenada  | result: success | dni: {client_data[DNI]} | numero: {client_data[NUMBER]}')
                n+=1
                self._agency_addr[int(client_data[CLIENT])] = addr
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
            with self._lock:
                self._agency_status[addr] = PENDING
            return addr
        except OSError:
            raise OSError
        
        
