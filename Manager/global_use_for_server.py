import os
import pickle
import random
import socket
import string
import struct
import time
import call_service


HOST = '0.0.0.0'
PORT = 49101
NUM_OF_SOCKETS_PER_CLIENT = 2
MAX_CLIENTS = 10 * NUM_OF_SOCKETS_PER_CLIENT
CLIENTS_COUNT = 0
CLIENTS_MAIN_KEY = {}  # CLIENTS_MAIN_KEY example: {sockets1: main_key1, sockets2: main_key2, etc..}
CLIENTS_NAME = {}  # CLIENTS_NAME example: {sockets1: username1, sockets2: username2, etc..}
TIME_LIMIT = 60  # 60 seconds to log in with a code.
CLIENTS_REMAINING_TIME = {}  # remaining time till timeout. for example: {(socket1, socket2): 4, (socket3, socket4): 20}
server_socket = None  # for main server
server_socket_call_service = None  # for inner server, who's responsible for calls from any kind.
SMTP_SERVER = None
MAIL_SENDER = 'lirazcyberproject@gmail.com'
MAIL_PASSWORD = 'ylgq ihxa fhgj rxwb'

SEPARATOR = b":::::::::"  # to separate between the cipher, tag, and nonce
CHUNK = 1024


def recv_data(conn, bytes_num: int, wait: float, decode=True):
    """
    Receives a specific number of bytes from the socket, with a timeout mechanism
    to ensure that the socket is synchronized and data is received regardless of when it was sent.

    :param conn: The socket object representing the client connection.
    :param bytes_num: The number of expected bytes to receive from the socket.
    :param wait: The timeout duration (in seconds) to wait for data before retrying.
    :param decode: A boolean indicating whether to decode the received data from bytes to a string.
    :return: The received data, decoded to a string if decode is True, otherwise returned as bytes.
    """
    conn.settimeout(wait)
    while True:
        try:
            # testing_functions(file_path, f"[CALL_SERVICE]: [SENDER] I'm: {CLIENTS_NAME[client_sockets]}. --> Waiting for Receive.. time: {datetime.datetime.now()}")
            data = conn.recv(bytes_num)
            if data:
                conn.settimeout(None)  # back to default.
                if decode:
                    data = data.decode()
                return data
        except socket.timeout:
            # testing_functions(file_path, f"[CALL_SERVICE]: [SENDER] I'm: {CLIENTS_NAME[client_sockets]}. Timed out while receiving data.time: {datetime.datetime.now()}")
            continue


def send_frame(conn, frame):
    # print(f"[GLOBAL_USE]: about to sending frame")
    try:
        message_data = pickle.dumps(frame)
        message_size = struct.pack("!I", len(message_data))

        conn.sendall(message_size)
        conn.sendall(message_data)
        return True
    except Exception as e:
        print(f"[GLOBAL_USE_FOR_SERVER]: failed to send frame - {e}")
        return False


def receive_frame(conn):
    try:
        message_size_data = recv_data(conn, 4, 0.001, False)
        if not message_size_data:
            return None
        message_size = struct.unpack(">L", message_size_data)[0]
        message_data = b""
        while len(message_data) < message_size:
            packet = recv_data(conn, message_size - len(message_data), 0.001, False)
            if not packet:
                return None
            message_data += packet
        frame = pickle.loads(message_data)
        return frame
    except:
        print(f"[GLOBAL_USE_FOR_CLIENT]: failed to receive frame")
        return None


def generate_id(num: int, usage="login verification"):
    """
    This function is creating a unique id for a call.
    :param num: int. length of id.
    :param usage: string. "call"/"login verification".
    :return: Nothing.
    """
    if "call" in usage:
        while True:
            number = ''.join(random.choices(string.digits, k=num))
            if number not in call_service.CLIENTS_STREAMS.keys():
                return number
            else:
                continue
    else:
        number = ''.join(random.choices(string.digits, k=num))
        return number


def handle_unauthenticated_clients():
    """
    This function handles clients remain time by modifying CLIENTS_REMAINING_TIME.
    :return: Nothing.
    """
    while True:
        while True:
            CLIENTS_REMAINING_TIME_copy = CLIENTS_REMAINING_TIME.copy()
            for client_sockets in CLIENTS_REMAINING_TIME_copy:  # run on all client sockets
                if CLIENTS_REMAINING_TIME[client_sockets] > 0:
                    CLIENTS_REMAINING_TIME[client_sockets] -= 1
            print("Updated CLIENTS_REMAINING_TIME:", CLIENTS_REMAINING_TIME)

            time.sleep(1)  # Pause execution for 1 second


def testing_functions(file_path, print):
    """
    This function is saving printings inside a file.
    :param file_path: string
    :param print: string
    :return: Nothing.
    """
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            pass

    with open(file_path, 'a') as file:
        file.write(print + '\n')


def clear_file(path):
    if os.path.exists(path):
        with open(path, 'w') as file:
            file.truncate(0)
            print("File cleared successfully.")
    else:
        print("File does not exist.")





