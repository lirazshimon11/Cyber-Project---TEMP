import datetime
import threading
import time
import numpy as np
import global_use_for_server


CLIENTS_ACTIVE = {}  # example: {client_sockets1: True, client_sockets2: False, etc...}
CLIENTS_STREAMS = {}  # example: {id1: {client_socket1: {"video": frame1, "voice": voice, "share screen": frame2}, client_socket2: {"video": frame} }, id2: {}}
exceptable_stream_types = ["video", "share screen", "voice", "external control", "events", "default"]


def printing():
    global CLIENTS_STREAMS
    while True:  # run as long as client is sending frames.
        print(f"CLIENTS_STREAMS --> {CLIENTS_STREAMS}")
        time.sleep(1)
        # pass


def isExist(client_sockets):
    global CLIENTS_ACTIVE
    if CLIENTS_ACTIVE == {} or client_sockets not in CLIENTS_ACTIVE.keys():
        print(f"[CALL_SERVICE]: updating to False.")
        CLIENTS_ACTIVE[client_sockets] = False
    return CLIENTS_ACTIVE[client_sockets]


def find_id_by_sockets(client_sockets):
    global CLIENTS_STREAMS
    for stream_id, sockets in CLIENTS_STREAMS.items():
        for socket, _ in sockets.items():
            if socket == client_sockets:
                return stream_id
    return None


def find_socket_by_name(username):
    """
    This function is getting a username.
    :param username: string
    :return: socket
    """
    # CLIENTS_NAME --> {socket1: username1, socket2: username2}
    for socket_conn, user in global_use_for_server.CLIENTS_NAME.items():
        if user == username:
            return socket_conn
    return None


def receive_streams(client_sockets, client_socket, stream_id):
    """
    This function receives and saves all client's streams (video, voice, share_screen).
    :param client_sockets: tuple of both sockets
    :param client_socket: socket
    :param stream_id: string. for example "0123456789"
    :return: Nothing.
    """
    global CLIENTS_ACTIVE, CLIENTS_STREAMS
    while CLIENTS_ACTIVE[client_sockets]:  # call is still on...
        try:
            if (CLIENTS_STREAMS[stream_id][client_sockets]["video"] is None and
                    CLIENTS_STREAMS[stream_id][client_sockets]["default"] is None):
                global_use_for_server.testing_functions(f"test_server_receiver_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [RECEIVER] user: {global_use_for_server.CLIENTS_NAME[client_sockets]} changing to True. time: {datetime.datetime.now()}")
                CLIENTS_STREAMS[stream_id][client_sockets]["default"] = True

            global_use_for_server.testing_functions(f"test_server_receiver_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [RECEIVER] user: {global_use_for_server.CLIENTS_NAME[client_sockets]} SENDING GO1. time: {datetime.datetime.now()}")
            client_socket.send("GO1".encode())  # sending --> GO1.

            global_use_for_server.testing_functions(f"test_server_receiver_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [RECEIVER] user: {global_use_for_server.CLIENTS_NAME[client_sockets]} Waiting For Data (type of stream).. time: {datetime.datetime.now()}")
            data = global_use_for_server.recv_data(client_socket, 1024, 1)  # type of stream.

            global_use_for_server.testing_functions(f"test_server_receiver_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [RECEIVER] user: {global_use_for_server.CLIENTS_NAME[client_sockets]} client wants --> {data}. time: {datetime.datetime.now()}")

            if "video" in data:
                if "clear" not in data:
                    client_socket.send("GO2".encode())  # sending GO2
                    frame = global_use_for_server.receive_frame(client_socket)  # receiving frame from client.
                    if frame is None:
                        CLIENTS_ACTIVE[client_sockets] = False  # raise a flag to stop.
                        global_use_for_server.testing_functions(f"test_server_receiver_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [RECEIVER] user: {global_use_for_server.CLIENTS_NAME[client_sockets]} frame={frame}. time: {datetime.datetime.now()}")
                        break
                    CLIENTS_STREAMS[stream_id][client_sockets]["video"] = frame
                    CLIENTS_STREAMS[stream_id][client_sockets]["default"] = None
                else:  # no longer active
                    CLIENTS_STREAMS[stream_id][client_sockets]["video"] = None

            elif "voice" in data:
                if "clear" not in data:
                    data = global_use_for_server.recv_data(client_socket, global_use_for_server.CHUNK, 1)
                    if not data:
                        break
                    CLIENTS_STREAMS[stream_id][client_sockets]["voice"] = data
                else:  # no longer active
                    CLIENTS_STREAMS[stream_id][client_sockets]["voice"] = b""

            elif "share screen" in data:
                if "clear" not in data:
                    global_use_for_server.testing_functions(f"test_server_receiver_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [RECEIVER] user: {global_use_for_server.CLIENTS_NAME[client_sockets]} receiving share screen. time: {datetime.datetime.now()}")
                    client_socket.send("GO3".encode())  # sending GO3
                    frame = global_use_for_server.receive_frame(client_socket)  # receiving frame from client.
                    if frame is None:
                        CLIENTS_ACTIVE[client_sockets] = False  # raise a flag to stop.
                        global_use_for_server.testing_functions(f"test_server_receiver_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [RECEIVER] user: {global_use_for_server.CLIENTS_NAME[client_sockets]} Error: Failed to receive message. time: {datetime.datetime.now()}")
                        break
                    CLIENTS_STREAMS[stream_id][client_sockets]["share screen"] = frame
                    global_use_for_server.testing_functions(f"test_server_receiver_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [RECEIVER] user: {global_use_for_server.CLIENTS_NAME[client_sockets]} share screen received --> {frame} time: {datetime.datetime.now()}")

                else:  # no longer active
                    CLIENTS_STREAMS[stream_id][client_sockets]["share screen"] = None

            elif "external control" in data:
                if "clear" not in data:
                    global_use_for_server.testing_functions(f"test_server_receiver_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [RECEIVER] user: {global_use_for_server.CLIENTS_NAME[client_sockets]} authorized all participants to control his screen. time: {datetime.datetime.now()}")
                    CLIENTS_STREAMS[stream_id][client_sockets]["external control"]["status"] = True
                else:  # no longer active
                    # it's very important to reset the dictionary with {}, because if the status was just True, probably
                    # there were more keys and values inside this dictionary
                    CLIENTS_STREAMS[stream_id][client_sockets]["external control"] = {}
                    CLIENTS_STREAMS[stream_id][client_sockets]["external control"]["status"] = False
            elif "mouse" in data or "keyboard" in data:
                global_use_for_server.testing_functions(f"test_server_receiver_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt",  f"[CALL_SERVICE]: [RECEIVER] user: {global_use_for_server.CLIENTS_NAME[client_sockets]} receiving event. time: {datetime.datetime.now()}")
                # getting events by controller on a participant's share screen.
                socket_target = find_socket_by_name(data.split("::")[0])
                event = data.split("::")[1]
                global_use_for_server.testing_functions(f"test_server_receiver_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [RECEIVER] user: {global_use_for_server.CLIENTS_NAME[client_sockets]} event --> {event}, socket --> {socket_target}. time: {datetime.datetime.now()}")

                global_use_for_server.testing_functions(f"test_server_receiver_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [RECEIVER] user: {global_use_for_server.CLIENTS_NAME[client_sockets]} event BEFORE --> {CLIENTS_STREAMS[stream_id][socket_target]["events"]}. time: {datetime.datetime.now()}")
                CLIENTS_STREAMS[stream_id][socket_target]["events"].append(event)
                global_use_for_server.testing_functions(f"test_server_receiver_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [RECEIVER] user: {global_use_for_server.CLIENTS_NAME[client_sockets]} event AFTER --> {CLIENTS_STREAMS[stream_id][socket_target]["events"]}. time: {datetime.datetime.now()}")
            global_use_for_server.testing_functions(f"test_server_receiver_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [RECEIVER] user: {global_use_for_server.CLIENTS_NAME[client_sockets]} END OF ITERATION. time: {datetime.datetime.now()}")

        except ConnectionResetError:
            global_use_for_server.testing_functions(f"test_server_receiver_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [RECEIVER] user: {global_use_for_server.CLIENTS_NAME[client_sockets]} receive_stream --> [RECEIVER] Client disconnected unexpectedly. time: {datetime.datetime.now()}")
            client_socket.close()
            break
        except Exception as e:
            global_use_for_server.testing_functions(f"test_server_receiver_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [RECEIVER] user: {global_use_for_server.CLIENTS_NAME[client_sockets]} Error in receive_streams: {e}. time: {datetime.datetime.now()}")


def send_streams(client_sockets, client_socket_backup, stream_id):
    """
    This function sends all streams from the relevant id.
    REMEMBER: the socket I'm using for sending streams is client_socket_backup.
    :param client_sockets: tuple of sockets.
    :param client_socket_backup: socket
    :param stream_id: string. call identifier, for example: "0123456789"
    :return: Nothing.
    """
    global CLIENTS_ACTIVE, CLIENTS_STREAMS
    while CLIENTS_ACTIVE[client_sockets]:
        try:
            # sending all active streams from the stream id.
            # global_use_for_server.testing_functions("test_server_sender.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. CLIENTS_STREAMS[stream_id] --> {CLIENTS_STREAMS[stream_id]}. time: {datetime.datetime.now()}")

            for sockets, values in CLIENTS_STREAMS[stream_id].copy().items():
                global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[sockets]} START 1")
                for stream_type, stream in values.items():  # stream_type: video/voice/share screen/default
                    global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[sockets]} --> type --> {stream_type}, stream --> {stream}. time: {datetime.datetime.now()}")
                    if (
                            (isinstance(stream, (bytes, bytearray)) and stream != b'') or
                            (isinstance(stream, list) and any(stream)) or
                            (isinstance(stream, np.ndarray) and stream.size > 0) or
                            (isinstance(stream, bool) and stream) or
                            (isinstance(stream, dict) and 'status' in stream and stream['status'])
                       ):
                        global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[sockets]} --> {stream_type} IS ON. time: {datetime.datetime.now()}")

                        if stream_type in exceptable_stream_types:
                            if stream_type != "events" or client_socket_backup == sockets[1]:
                                authorization = global_use_for_server.recv_data(client_socket_backup, 3, 0.001)  # responsible for syncing with the client.
                                global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[sockets]} -->  AUTHORIZATION= {authorization}. time: {datetime.datetime.now()}")

                                message = f"{global_use_for_server.CLIENTS_NAME[sockets]}:{stream_type}"
                                global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[sockets]} --> message I'm about to send --> {message}. time: {datetime.datetime.now()}")
                                client_socket_backup.send(message.encode())
                                global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[sockets]} --> message sent successfully. time: {datetime.datetime.now()}")

                                if stream_type == "video":
                                    authorization = global_use_for_server.recv_data(client_socket_backup, 3, 0.001)  # responsible for syncing with the client.
                                    global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[sockets]} -->  AUTHORIZATION VIDEO= {authorization}. time: {datetime.datetime.now()}")

                                    global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[sockets]} --> start. time: {datetime.datetime.now()}")
                                    global_use_for_server.send_frame(client_socket_backup, stream)
                                    global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[sockets]} --> frame sent successfully! time: {datetime.datetime.now()}")
                                elif stream_type == "share screen":
                                    authorization = global_use_for_server.recv_data(client_socket_backup, 3, 0.001)  # responsible for syncing with the client.
                                    global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[sockets]} -->  AUTHORIZATION SHARE SCREEN= {authorization}. time: {datetime.datetime.now()}")

                                    global_use_for_server.send_frame(client_socket_backup, stream)
                                    global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[sockets]} --> frame sent successfully! time: {datetime.datetime.now()}")

                                    # authorization = global_use_for_server.recv_data(client_socket_backup, 3, 0.001)  # responsible for syncing with the client.
                                    # global_use_for_server.testing_functions("test_server_sender.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[sockets]} -->  AUTHORIZATION= {authorization}. time: {datetime.datetime.now()}")

                                elif stream_type == "voice":
                                    client_socket_backup.sendall(stream)

                                # elif stream_type == "external control":
                                #     client_socket_backup.send(message.encode())

                                elif stream_type == "events":  # no need to check the sockets... (already been checked)
                                    global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[sockets]} --> in events {CLIENTS_STREAMS}. time: {datetime.datetime.now()}")

                                    events = CLIENTS_STREAMS[stream_id][sockets]["events"]
                                    global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[sockets]} --> events --> {events}. time: {datetime.datetime.now()}")

                                    sent = True  # if--> f"{global_use_for_server.CLIENTS_NAME[sockets]}:{stream_type}" sent/not
                                    for event in events.copy():
                                        if not sent:
                                            authorization = global_use_for_server.recv_data(client_socket_backup, 3, 0.001)  # responsible for syncing with the client.
                                            global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[sockets]} -->  AUTHORIZATION= {authorization}. time: {datetime.datetime.now()}")
                                            global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt",f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about user: {global_use_for_server.CLIENTS_NAME[sockets]} --> [SENDER] I need to send message again. time: {datetime.datetime.now()}")
                                            client_socket_backup.send(message.encode())

                                        global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt",  f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[sockets]} --> sending the event --> {event}. time: {datetime.datetime.now()}")
                                                                                            # global_use_for_server.testing_functions("test_server_sender.txt",  f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[sockets]} --> sending the event --> {event}. time: {datetime.datetime.now()}")
                                        client_socket_backup.send(str(event).encode())
                                        CLIENTS_STREAMS[stream_id][sockets]["events"].remove(event)
                                        global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt",  f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[sockets]} --> event removed. time: {datetime.datetime.now()}")
                                        global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt",  f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[sockets]} --> array is now: {CLIENTS_STREAMS[stream_id][sockets]["events"]}. time: {datetime.datetime.now()}")
                                        sent = False
                                global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[sockets]} --> AFTER IF'S. time: {datetime.datetime.now()}")
                                # elif stream_type == "default":
                                #     client_socket_backup.send(message.encode())

                        global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[client_sockets]} END 1. time: {datetime.datetime.now()}")
                    global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[client_sockets]} END 2. time: {datetime.datetime.now()}")
                global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  user: {global_use_for_server.CLIENTS_NAME[client_sockets]} END 3. time: {datetime.datetime.now()}")
        except ConnectionResetError:
            global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]}. talking about  send_stream --> Client disconnected unexpectedly. time: {datetime.datetime.now()}")
            client_socket_backup.close()
            break
        except Exception as e:
            global_use_for_server.testing_functions(f"test_server_sender_{global_use_for_server.CLIENTS_NAME[client_sockets]}.txt", f"[CALL_SERVICE]: [SENDER] I'm: {global_use_for_server.CLIENTS_NAME[client_sockets]} Error in sending. {e}. time: {datetime.datetime.now()}")


def handle_client(prev_client_sockets, stream_id="0123456789"):
    global CLIENTS_ACTIVE, CLIENTS_STREAMS
    client_socket, client_address = global_use_for_server.server_socket_call_service.accept()
    client_socket_backup, client_address_backup = global_use_for_server.server_socket_call_service.accept()

    client_sockets = (client_socket, client_socket_backup)

    # UPDATING GLOBAL DICTIONARIES:
    global_use_for_server.CLIENTS_NAME[client_sockets] = global_use_for_server.CLIENTS_NAME[prev_client_sockets]  # updating the new key
    global_use_for_server.CLIENTS_MAIN_KEY[client_sockets] = global_use_for_server.CLIENTS_MAIN_KEY[prev_client_sockets]
    global_use_for_server.CLIENTS_NAME.pop(prev_client_sockets)  # deleting the unnecessary key (prev_client_sockets) from the names dictionary.
    global_use_for_server.CLIENTS_MAIN_KEY.pop(prev_client_sockets)  # deleting the unnecessary key (prev_client_sockets) from the keys dictionary.

    # Initialize data for client
    CLIENTS_ACTIVE[client_sockets] = True
    if stream_id not in CLIENTS_STREAMS:
        CLIENTS_STREAMS[stream_id] = {}

    CLIENTS_STREAMS[stream_id][client_sockets] = {
            "video": None,
            "voice": b"",
            "share screen": None,
            "external control": {"status": False},
            "events": [],
            "default": True
    }

    # print(f"after initializing --> {CLIENTS_STREAMS}")
    handle_client_thread = threading.Thread(target=receive_streams, args=(client_sockets, client_socket, stream_id, ))
    handle_client_thread.start()

    # in case the client will send 2 requests from different places at the exact same time.
    handle_client_thread_backup = threading.Thread(target=send_streams, args=(client_sockets, client_socket_backup, stream_id, ))
    handle_client_thread_backup.start()

    global_use_for_server.CLIENTS_COUNT += 1

    printing()