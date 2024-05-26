import ast
import os
import threading
import time
from functools import partial
import customtkinter
import encryption_decryption
from PIL import Image, ImageTk
from CTkListbox import *
import call_handler
import global_use_for_client

# GLOBALS:
global canvas, PREV_CHAT_CONTENT, self_stream_thread, end_video_call_button, my_last_frame, \
    friend_label

PREV_CHAT_CONTENT = {}  # supposed to always have the previous chat content in order to now if update is needed.
chat_update_thread = None  # Thread for updating the chat
stop_video_stream = False
self_stream_thread = None
my_last_frame = None
friend_label = None


def main(canvas_):
    """
    This function's purpose is to display all friends related functions (for example: chat, calls, etc.)
    :return: Nothing.
    """
    global canvas, chat_update_thread

    canvas = canvas_

    print("in show friends")
    message = {"request": "get friends"}
    encryption_decryption.protocol_send_for_client(global_use_for_client.server_socket, message, global_use_for_client.MAIN_KEY)  # sending --> request and all he needs to

    response = encryption_decryption.receive_message(global_use_for_client.server_socket, global_use_for_client.MAIN_KEY)  # receiving --> response to my request
    try:
        y = 62
        if "EMPTY" not in response:
            response_to_array = response.split("\n")
            print(f"[FRIENDS_FUNCTIONALITY]: friends are {response_to_array}")

            for friend in response_to_array:
                print(f"[FRIENDS FUNCTIONALITY]: about to 'create' the friend- {friend}")
                if "," not in friend:  # not group
                    friend_button = customtkinter.CTkButton(master=global_use_for_client.ROOT, text=friend, fg_color="transparent", corner_radius=10,
                                                            height=50, text_color=global_use_for_client.TEXT_COLOR, font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE),
                                                            width=canvas.winfo_screenwidth()-333, anchor="w")

                    HOVER = global_use_for_client.HOVER_COLOR
                    friend_button.configure(hover_color=HOVER)
                    friend_button.place(x=global_use_for_client.X_ALIGNMENT, y=y)
                    open_chat_partial = partial(open_chat, friend)
                    friend_button.configure(command=open_chat_partial)
                else:  # group
                    print(f"friend={friend}, type={type(friend)}")
                    # Convert the string representation of the list into an actual list
                    my_list = ast.literal_eval(friend)

                    # Join the elements of the list with commas and spaces
                    group = ", ".join(my_list)
                    print(f"group is {group}")
                    friend_button = customtkinter.CTkButton(master=global_use_for_client.ROOT, text=group, fg_color="transparent",
                                                            corner_radius=10,
                                                            height=50, text_color=global_use_for_client.TEXT_COLOR,
                                                            font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE),
                                                            width=canvas.winfo_screenwidth() - 333, anchor="w")

                    HOVER = global_use_for_client.HOVER_COLOR
                    friend_button.configure(hover_color=HOVER)
                    friend_button.place(x=global_use_for_client.X_ALIGNMENT, y=y)
                    open_chat_partial = partial(open_chat, group)
                    friend_button.configure(command=open_chat_partial)

                # voice call button
                voice_call_partial = partial(start_call, friend, "voice")
                voice_call_image = customtkinter.CTkImage(light_image=Image.open(fr"{os.getcwd()}\Pictures\voice_call.png"),
                                                          size=(50, 50))
                voice_call_button = customtkinter.CTkButton(master=global_use_for_client.ROOT, text="", width=50, image=voice_call_image,
                                                            command=voice_call_partial, fg_color="transparent",
                                                            hover_color=global_use_for_client.HOVER_COLOR)
                voice_call_button.place(x=int(global_use_for_client.add_friends_button.place_info()["x"]) + 35,
                                        y=y + friend_button.winfo_height() - 5)

                # video call button
                video_call_partial = partial(start_call, friend, "video")

                video_call_image = customtkinter.CTkImage(light_image=Image.open(fr"{os.getcwd()}\Pictures\video_call.png"),
                                                          size=(50, 50))
                video_call_button = customtkinter.CTkButton(master=global_use_for_client.ROOT, text="", width=50, image=video_call_image,
                                                            command=video_call_partial, fg_color="transparent",
                                                            hover_color=global_use_for_client.HOVER_COLOR)
                video_call_button.place(x=int(voice_call_button.place_info()["x"]) + 66,
                                        y=y + friend_button.winfo_height() - 5)

                y += friend_button.winfo_height() + 55

        else:  # FRIENDS BOX IS EMPTY
            friend_button = customtkinter.CTkButton(master=global_use_for_client.ROOT, text=response, fg_color="transparent", corner_radius=10,
                                                    height=50, text_color=global_use_for_client.TEXT_COLOR, font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE),
                                                    width=canvas.winfo_screenwidth() - 333, anchor="w")
            HOVER = global_use_for_client.BACKGROUND_COLOR
            friend_button.configure(hover_color=HOVER)
            friend_button.pack()
            friend_button.place(x=global_use_for_client.X_ALIGNMENT, y=y)
    except Exception as e:
        print(f"[FRIENDS_FUNCTIONALITY]: error: {e}")


def open_chat(friends):
    import home
    global PREV_CHAT_CONTENT, canvas, chat_update_thread

    # if global_use_for_client.ROOT is not None:
    #     global_use_for_client.ROOT = tk.Tk()

    home.home_structure()

    print(f"[FRIENDS FUNCTIONALITY]: in open_chat - {friends}")
    global_use_for_client.is_on_chat_screen = True  # Set the flag to True when opening the chat
    PREV_CHAT_CONTENT = {}

    # Start the chat update thread
    chat_update_thread = threading.Thread(target=update_chat, args=(friends,))
    chat_update_thread.start()

    MAX_CHARS = 80
    friends_text = friends
    if len(friends) > MAX_CHARS:
        friends_text = f"{friends[0:MAX_CHARS-3]}..."  # the -3 is because of the "..."
    friend_label = customtkinter.CTkButton(master=global_use_for_client.ROOT, text=friends_text, fg_color=global_use_for_client.BACKGROUND_COLOR,
                                           font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE),
                                           hover_color=global_use_for_client.BACKGROUND_COLOR, text_color=global_use_for_client.TEXT_COLOR,
                                           height=50, anchor="w")
    friend_label.pack(padx=3, pady=1)
    friend_label.place(x=global_use_for_client.X_ALIGNMENT + 10, y=10)

    global_use_for_client.send_msg_entry = customtkinter.CTkEntry(master=global_use_for_client.ROOT, font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE),
                                                                  corner_radius=10, width=1200, height=50, placeholder_text=f"Message {friends_text}..", validate="key",
                                                                  validatecommand=(global_use_for_client.ROOT.register(lambda text: len(text) <= global_use_for_client.MAX_CHARACTERS_AMOUNT), "%P"))
    global_use_for_client.send_msg_entry.place(x=global_use_for_client.X_ALIGNMENT + 10, y=724)

    global_use_for_client.send_msg_entry.bind("<Return>", lambda event: send_message(friends))


def update_chat(friends):
    while global_use_for_client.is_on_chat_screen:
        show_chat(friends)
        time.sleep(2)


def show_chat(friend):
    global canvas, PREV_CHAT_CONTENT
    print(f"[FRIENDS FUNCTIONALITY]: in show_private_chat. friend is {friend}")
    message = {"request": "get private chat", "friends": friend}
    encryption_decryption.protocol_send_for_client(global_use_for_client.server_socket, message, global_use_for_client.MAIN_KEY)  # sending --> request and all he needs to

    chat = encryption_decryption.receive_message(global_use_for_client.server_socket, global_use_for_client.MAIN_KEY, "dictionary")
    if chat and PREV_CHAT_CONTENT != chat:  # if has changed.
        print(f"[FRIENDS FUNCTIONALITY]: THE CHAT CONTENT HAS BEEN CHANGED. THIS IS THE CURRENT CONTENT--> {chat}")

        messages_list = CTkListbox(global_use_for_client.ROOT)

        messages_list.configure(width=int(global_use_for_client.add_friends_button.place_info()["x"]) + 120 - global_use_for_client.X_ALIGNMENT,
                                height=int(global_use_for_client.send_msg_entry.place_info()["y"]) - global_use_for_client.send_msg_entry.winfo_height() - 50,
                                text_color=global_use_for_client.TEXT_COLOR, font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE),
                                hover_color=global_use_for_client.BACKGROUND_COLOR)
        messages_list.pack(fill="both", expand=True)
        messages_list.place(x=global_use_for_client.X_ALIGNMENT+10, y=70)

        for detail in chat:
            message = detail['sender'] + ": " + detail['message']
            print(f"[FRIENDS FUNCTIONALITY]: message={message}")
            messages_list.insert("end", message)
        PREV_CHAT_CONTENT = chat  # update the chat content for the next checking.
    else:
        print(f"[FRIENDS FUNCTIONALITY]: the chat hasn't changed so update isn't needed.")


def send_message(friends=None):
    """
    :param friends:
    :return:
    """
    print(f"[FRIENDS FUNCTIONALITY]: in send_message. friend is {friends}")

    msg = global_use_for_client.send_msg_entry.get()
    global_use_for_client.send_msg_entry.delete(0, 'end')  # useless so deleting.
    message = {"request": "set private chat", "receiver": friends, "message": msg}
    encryption_decryption.protocol_send_for_client(global_use_for_client.server_socket, message, global_use_for_client.MAIN_KEY)  # sending --> request and all he needs to

    # server_socket.send(encryption_decryption.encrypt_msg_for_client(message, MAIN_KEY))
    # cleaning entry:
    show_chat(friends)


def list_convertor(people):
    if isinstance(people, str):
        # Check if the string represents a list
        if people.startswith("[") and people.endswith("]"):
            # Attempt to evaluate the string as a list
            try:
                converted_list = eval(people)
                if isinstance(converted_list, list):
                    return converted_list
                else:
                    return [people]  # If it's not a valid list, return the string in a list
            except SyntaxError:
                return [people]  # If it's not a valid list representation, return the string in a list
        else:
            return [people]  # If it's a regular string, return it in a list
    elif isinstance(people, list):
        return people  # If it's already a list, return it as is
    else:
        return None  # If it's neither a string nor a list, return None


def start_call(friends, call_type):
    """
    This function sends a request to the server to start a call with the given friends.
    Finally, initiates the call handler. (with the new GUI)

    :return: Nothing.
    """
    global_use_for_client.ROOT.destroy()
    global_use_for_client.call_mode = True

    friends = list_convertor(friends)
    print(f"[FRIENDS_FUNCTIONALITY]: friend --> {friends}")

    message = {"request": "start call", "friends": friends}
    encryption_decryption.protocol_send_for_client(global_use_for_client.server_socket, message, global_use_for_client.MAIN_KEY)

    message = {"request": "start call"}
    encryption_decryption.protocol_send_for_client(global_use_for_client.server_socket_backup, message, global_use_for_client.MAIN_KEY)

    global_use_for_client.server_socket.close()
    global_use_for_client.server_socket_backup.close()

    call_handler.main(call_type)

