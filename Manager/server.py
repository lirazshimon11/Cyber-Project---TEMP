#                    IMPORTS                    #
import threading as threading
import socket
import encryption_decryption
from application_users import Users
import call_service
import psutil
import global_use_for_server
import email_sender
import time
################################################

#                     GLOBAL                     #
global WAIT_FOR_AUTHORIZATION
WAIT_FOR_AUTHORIZATION = 3  # the max number of seconds I'm willing to wait is 20 seconds
##############################################


def login_or_registering(client_sockets, client_socket, data):
    """
    This function's purpose is to handle login and registrations.
    :param client_sockets: tuple of 2 sockets.
    :param client_socket: socket
    :param data: dictionary.
    :return: Nothing
    """
    global WAIT_FOR_AUTHORIZATION
    print(f"[SERVER]: in login_or_registering")
    print(f"dictionary: {data}")
    u = Users()
    if data["request"] == "login":  # request + login:
        print(data['username'], data['password'])
        if u.check_exist(data['username'], data['password']):
            encryption_decryption.protocol_send_for_server(client_socket, "NEED CODE", global_use_for_server.CLIENTS_MAIN_KEY[client_sockets])  # sending --> letting the client know what
            code = global_use_for_server.generate_id(6, "login verification")
            if email_sender.send_mail(code, u.get_email(data['username'])):
                encryption_decryption.protocol_send_for_server(client_socket, "EMAIL SENT!", global_use_for_server.CLIENTS_MAIN_KEY[client_sockets])  # sending --> letting the client know what
                global_use_for_server.CLIENTS_REMAINING_TIME[client_sockets] = global_use_for_server.TIME_LIMIT
                response = None
                while global_use_for_server.CLIENTS_REMAINING_TIME[client_sockets] > 0 and code != response:
                    print(f"adding to remaining time!")
                    try:
                        response = encryption_decryption.receive_message(client_socket, global_use_for_server.CLIENTS_MAIN_KEY[client_sockets], WAIT_FOR_AUTHORIZATION)
                        print(f"[SERVER]: code? he sent-->{response}")
                        if code == response:
                            encryption_decryption.protocol_send_for_server(client_socket, "AUTHORIZED", global_use_for_server.CLIENTS_MAIN_KEY[client_sockets])  # sending --> letting the client know what
                            global_use_for_server.CLIENTS_NAME[client_sockets] = data["username"]
                            global_use_for_server.CLIENTS_REMAINING_TIME.pop(client_sockets)

                        else:
                            encryption_decryption.protocol_send_for_server(client_socket, "NO", global_use_for_server.CLIENTS_MAIN_KEY[client_sockets])  # sending --> letting the client know what

                    except Exception as e:  # TIMES UP.
                        print(f"[SERVER]: TIME IS UP!!!!! {e}")
                        encryption_decryption.protocol_send_for_server(client_socket, "NO", global_use_for_server.CLIENTS_MAIN_KEY[client_sockets])  # sending --> letting the client know what
                print(f"[SERVER]: TIME IS UP.")
            else:
                encryption_decryption.protocol_send_for_server(client_socket, "INCORRECT EMAIL", global_use_for_server.CLIENTS_MAIN_KEY[client_sockets])  # sending --> letting the client know what
        else:
            encryption_decryption.protocol_send_for_server(client_socket, "NO", global_use_for_server.CLIENTS_MAIN_KEY[client_sockets])  # sending --> letting the client know what

    else:  # register:
        if not u.check_exist(data['username'], data['password']):  # if he doesn't exist
            print(data['full_name'], data['email'], data['username'], data['password'], data['phone_number'])
            result = u.insert_user(data['full_name'], data['email'], data['username'], data['password'], data['phone_number'])
            encryption_decryption.protocol_send_for_server(client_socket, result, global_use_for_server.CLIENTS_MAIN_KEY[client_sockets])  # sending --> letting the client know what
        else:
            encryption_decryption.protocol_send_for_server(client_socket, "NO", global_use_for_server.CLIENTS_MAIN_KEY[client_sockets])  # sending --> letting the client know what


def kill_process_by_name(process_name):
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            print(f"Killing process {proc.info['pid']}: {proc.info['name']}")
            proc.kill()


def FOR_TESTING():
    """
    This function is FOR TESTING ONLY. the purpose of this testing is for me to not register each and every time.
    :return: NOTHING.
    """
    u = Users()
    try:
        kill_process_by_name("DB Browser for SQLite.exe")
        u.delete_database()
    except:
        print("Resetting didn't work properly..")
    time.sleep(1)
    u = Users()
    if not u.check_exist("a", "a"):
        u.insert_user("a a", "lirazshimon@gmail.com", "a", "a", "1")
        u.insert_user("b b", "lirazshimon4@gmail.com", "b", "b", "2")
        u.insert_user("c c", "c@gmail.com", "c", "c", "3")
        u.insert_user("d d", "d@gmail.com", "d", "d", "4")
        u.insert_user("e e", "e@gmail.com", "e", "e", "5")
        # u.insert_user("t t", "t@gmail.com", "t", "t", 5)
        u.insert_user("oran shimon", "oranshimon@gmail.com", "oranshimon", "oranshimon", "5")
        u.insert_user("liraz shimon", "liraz@gmail.com", "lirazshimon11", "lirazshimon11", "0528188817")

        u.set_both_friends("a", "b")
        u.set_both_friends("a", "c")
        u.set_both_friends("a", "d")
        u.set_both_friends("a", "lirazshimon11")
        u.set_both_friends("lirazshimon11", "oranshimon")
        # u.set_group_chat("a", "b", "a, b, c", "what's going on1")
        # print("after")
        # u.set_both_private_chat("b", "a", "hey what's up1")
        # u.set_both_private_chat("c", "a", "hey what's up2")
        print("------------------------------------------------------------------")
        # u.set_group_chat("a", "b", "a, b, c", "what's going on1")
        # u.set_group_chat("a", "a", "a, b, c", "what's going on2")
        # u.set_group_chat("a", "c", "a, b, c", "what's going on3")


def handle_sending_follow_requests(client_sockets, client_socket, username_target):
    u = Users()
    if u.check_exist_username(username_target) and username_target not in u.get_friends(global_use_for_server.CLIENTS_NAME[client_sockets]) and username_target != global_use_for_server.CLIENTS_NAME[client_sockets]:
        u.set_notifications(username_target, f"{global_use_for_server.CLIENTS_NAME[client_sockets]} requested to follow you")
        encryption_decryption.protocol_send_for_server(client_socket, "Sent!", global_use_for_server.CLIENTS_MAIN_KEY[client_sockets])  # sending --> letting the client know what
        print(f"[SERVER]: setting notifications went perfectly!")
    else:  # username doesn't exist or they are already following each other.
        encryption_decryption.protocol_send_for_server(client_socket, "Hm, didn't work. Double check that the username is correct.", global_use_for_server.CLIENTS_MAIN_KEY[client_sockets])  # sending --> letting the client know what


def handle_create_group(username, group):
    """
    This function gets a username (the initiator) and the group that the username want to create.
    the function runs on each friend in the group and set his notification if needed, and set his personal details.
    for example: username="a", group=["a", "b", "c"]:
                 I'll append "["a", "b", "c"]" inside each participant's friends information
    :param username: string
    :param group: list
    :return: Nothing
    """
    print(f"[SERVER]: in handle_create_group")
    u = Users()
    for friend in group:  # runs all group friends
        print(f"[SERVER]: friend is {friend}. username={username}")
        if friend != username:
            u.set_notifications(friend, f"{username} created a new group!")
        u.set_group(friend, group)  # set details for each friend


def notify_friends(initiator, friends, call_id):
    """
    This function's purpose is to set notifications and important notifications for a couple of users.
    :param initiator: string. (no need to set things for him)
    :param friends: list.
    :param call_id: string. so the invitees would be able to join the call.
    :return: Nothing.
    """
    u = Users()
    for friend in friends:
        if friend != initiator:
            u.set_notifications(friend, f"{initiator}:Incoming Call..")
            u.set_important(friend, f"{initiator}:Incoming Call..:{call_id}")


def handle_request(client_sockets, client_socket):
    """
    This function's purpose is to handle each client's requests.
    :param client_sockets: tuple or sockets. (socket1, socket2)
    :param client_socket: socket
    :return: Nothing
    """
    print(f"[SERVER]: in handle_request\n [SERVER]: client socket is {client_socket}")
    u = Users()
    try:
        while True:
            data = {"request": "Nothing"}
            if call_service.isExist(client_sockets) is False:
                print(f"[SERVER]: okay to receive.")
                data = encryption_decryption.receive_message(client_socket, global_use_for_server.CLIENTS_MAIN_KEY[client_sockets], "dictionary")

            if data is None:
                print(f"[SERVER]: No data received. Client may have disconnected. {client_socket}")
                break

            print(f"[SERVER]: data is --> {data}\n")
            try:
                if data["request"] == "login" or data["request"] == "register":
                    login_or_registering(client_sockets, client_socket, data)
                elif data["request"] == "time":
                    if client_sockets in global_use_for_server.CLIENTS_REMAINING_TIME:
                        print(f"already exists in dictionary. {global_use_for_server.CLIENTS_REMAINING_TIME}")
                        time_remain = global_use_for_server.CLIENTS_REMAINING_TIME[client_sockets]
                    else:
                        time_remain = global_use_for_server.TIME_LIMIT
                    encryption_decryption.protocol_send_for_server(client_socket, f"{time_remain}",
                                                                       global_use_for_server.CLIENTS_MAIN_KEY[client_sockets])

                elif "get" in data["request"]:
                    if "notifications" in data["request"]:
                        notifications = u.get_notifications(global_use_for_server.CLIENTS_NAME[client_sockets])
                        if notifications == "":
                            encryption_decryption.protocol_send_for_server(client_socket, "NOTIFICATION BOX IS EMPTY.", global_use_for_server.CLIENTS_MAIN_KEY[client_sockets])
                        else:
                            encryption_decryption.protocol_send_for_server(client_socket, notifications, global_use_for_server.CLIENTS_MAIN_KEY[client_sockets])
                    elif "friends" in data["request"]:
                        friends = u.get_friends(global_use_for_server.CLIENTS_NAME[client_sockets])
                        if friends == "":
                            encryption_decryption.protocol_send_for_server(client_socket, "FRIENDS BOX IS CURRENTLY EMPTY.", global_use_for_server.CLIENTS_MAIN_KEY[client_sockets])
                        else:
                            encryption_decryption.protocol_send_for_server(client_socket, friends, global_use_for_server.CLIENTS_MAIN_KEY[client_sockets])
                    elif "private chat" in data["request"]:
                        chat = u.get_private_chat(global_use_for_server.CLIENTS_NAME[client_sockets], data["friends"])
                        if chat is None or chat == {}:  # EMPTY
                            chat = {}  # shouldn't it be in a dictionary to work ???
                        encryption_decryption.protocol_send_for_server(client_socket, chat, global_use_for_server.CLIENTS_MAIN_KEY[client_sockets], "dictionary")
                    elif "important" in data["request"]:
                        important = u.get_important(global_use_for_server.CLIENTS_NAME[client_sockets])
                        if important == "":
                            encryption_decryption.protocol_send_for_server(client_socket, "EMPTY", global_use_for_server.CLIENTS_MAIN_KEY[client_sockets])
                        else:
                            encryption_decryption.protocol_send_for_server(client_socket, important, global_use_for_server.CLIENTS_MAIN_KEY[client_sockets])
                    elif "usernames" in data["request"]:  # currently for testing.
                        usernames = u.get_usernames()
                        if usernames == "":
                            encryption_decryption.protocol_send_for_server(client_socket, "EMPTY", global_use_for_server.CLIENTS_MAIN_KEY[client_sockets])
                        else:
                            encryption_decryption.protocol_send_for_server(client_socket, usernames, global_use_for_server.CLIENTS_MAIN_KEY[client_sockets])

                elif "set" in data["request"]:
                    if data["request"] == "set private chat":
                        if "," not in data["receiver"]:  # private chat
                            u.set_both_private_chat(global_use_for_server.CLIENTS_NAME[client_sockets], data["receiver"], data["message"])
                        else:  # group chat
                            print(f"[SERVER]: to--> {data["receiver"]} type is {type(data["receiver"])}")
                            for username in data["receiver"].split(", "):  # go through each user from the group
                                print(f"[SERVER]: {username}")
                                u.set_group_chat(username, data["sender"], data["receiver"], data["message"])
                    elif "username" in data["request"]:  # FOR TESTING!
                        global_use_for_server.CLIENTS_NAME[client_sockets] = data["username"]

                elif "start call" in data["request"]:
                    if client_socket == client_sockets[1]:
                        print("here1")
                        u.clear_important(global_use_for_server.CLIENTS_NAME[client_sockets])
                    else:
                        if "id" not in data:  # this is the initiator.
                            print("here3")
                            stream_id = global_use_for_server.generate_id(10, "call")
                            notify_friends(global_use_for_server.CLIENTS_NAME[client_sockets], data["friends"], stream_id)
                        else:
                            stream_id = data["id"]
                        client_socket.close()
                        call_service.handle_client(client_sockets, stream_id)
                        print(f"OUT OF CALL !!")
                    break
                elif data["request"] == "clean important":
                    u.clear_important(global_use_for_server.CLIENTS_NAME[client_sockets])
                elif data["request"] == "accept friend":  # data["username"] --> the initiator
                    u.set_both_friends(global_use_for_server.CLIENTS_NAME[client_sockets], data["username"])
                    u.set_notifications(data["username"], f"{global_use_for_server.CLIENTS_NAME[client_sockets]} accepted your request, you are now friends!")
                    print(f"[SERVER]: both users are now friends!")

                elif data["request"] == "friendship request":
                    handle_sending_follow_requests(client_sockets, client_socket, data["username"])
                elif data["request"] == "create group":
                    handle_create_group(global_use_for_server.CLIENTS_NAME[client_sockets], data["group"])
            except EOFError:
                print("[SERVER]: Client disconnected unexpectedly.")
                break  # Break out of the loop to close the socket and perform cleanup
            except Exception as e:
                print(f"[SERVER]: something is wrong with data: {e}")
                time.sleep(0.3)
    finally:
        if client_socket == client_sockets[0]:  # when the call will end, then all of these will be changed. (I'm using these variables in the call handler)
            global_use_for_server.CLIENTS_COUNT -= 1
            # global_use_for_server.CLIENTS_NAME.pop(client_sockets)
            # global_use_for_server.CLIENTS_MAIN_KEY.pop(client_sockets)
        client_socket.close()
        # threading.current_thread().join()
        return


def handle_client():
    print("in handle_client")
    client_socket, client_address = global_use_for_server.server_socket.accept()
    client_socket_backup, client_address_backup = global_use_for_server.server_socket.accept()
    print(f"[SERVER]: client socket is {client_socket}")

    key = encryption_decryption.handle_keys_exchange_for_server(client_socket)

    client_sockets = (client_socket, client_socket_backup)
    global_use_for_server.CLIENTS_MAIN_KEY[client_sockets] = key
    print(f"[SERVER]: current CLIENTS: {global_use_for_server.CLIENTS_MAIN_KEY}\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

    handle_client_thread = threading.Thread(target=handle_request, args=(client_sockets, client_socket, ))
    handle_client_thread.start()

    handle_client_thread_backup = threading.Thread(target=handle_request, args=(client_sockets, client_socket_backup,))
    handle_client_thread_backup.start()

    global_use_for_server.CLIENTS_COUNT += 1


def main():
    FOR_TESTING()  # starting testing function.
    while global_use_for_server.CLIENTS_COUNT < global_use_for_server.MAX_CLIENTS:
        try:
            handle_client()
        except Exception as e:
            print(f"[SERVER]: Error accepting client connection: {e}")


# asyncio.run(main())
def init_server():
    """
    This function is creating main server and inner server (for calls)
    :return: Nothing.
    """
    # Create server socket
    global_use_for_server.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    global_use_for_server.server_socket.bind((global_use_for_server.HOST, global_use_for_server.PORT))
    global_use_for_server.server_socket.listen(global_use_for_server.MAX_CLIENTS)
    print(f"Server listening on {global_use_for_server.HOST}:{global_use_for_server.PORT}")

    global_use_for_server.PORT = 56561
    # Create server socket
    global_use_for_server.server_socket_call_service = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    global_use_for_server.server_socket_call_service.bind((global_use_for_server.HOST, global_use_for_server.PORT))
    global_use_for_server.server_socket_call_service.listen(global_use_for_server.MAX_CLIENTS)
    print(f"Server listening on {global_use_for_server.HOST}:{global_use_for_server.PORT}")

    email_sender.init_smtp_server()

    time_handler = threading.Thread(target=global_use_for_server.handle_unauthenticated_clients, )
    time_handler.start()  # handles clients authentication time limit

    global_use_for_server.clear_file("test_server_receiver_a.txt")
    global_use_for_server.clear_file("test_server_receiver_b.txt")
    global_use_for_server.clear_file("test_server_sender_a.txt")
    global_use_for_server.clear_file("test_server_sender_b.txt")


if __name__ == "__main__":
    init_server()

    main()
