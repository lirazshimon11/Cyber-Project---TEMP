# IMPORTS:
import socket
import threading
import time
from functools import partial
from tkinter import *
from PIL import Image, ImageTk
import tkinter as tk
import os
import customtkinter
import encryption_decryption
import notifications_display
import add_friend_display
import create_group_display
import discover_display
import friends_functionality
import call_handler
import global_use_for_client

# GLOBALS:
global canvas

IMPORTANT_FRAME = None


def wait_for_important():
    """
    This function continuously checks for important notifications, such as incoming calls, from the server.
    It does not take any input and runs indefinitely until a certain condition is met.

    The function operates by sending a request to the server to retrieve important notifications
    every few seconds. If an important notification is received, it processes the notification
    using the `run_important` function. If no important notification is received (indicated by
    the server responding with "EMPTY"), it handles this condition appropriately.

    The function exits its loop and stops checking for notifications if the global flag
    `call_mode` is set to True.
    :return: Nothing.
    """
    while True:
        if global_use_for_client.call_mode is False:
            try:
                message = {"request": "get important"}
                encryption_decryption.protocol_send_for_client(global_use_for_client.server_socket_backup, message,
                                                               global_use_for_client.MAIN_KEY)

                data = encryption_decryption.receive_message(global_use_for_client.server_socket_backup,
                                                             global_use_for_client.MAIN_KEY)
                if data and data != "EMPTY":  # important contains something.
                    run_important(data)
                else:  # EMPTY:
                    print(f"{global_use_for_client.FILE_NAME}: important is EMPTY.{IMPORTANT_FRAME}")
                    try:
                        IMPORTANT_FRAME.destroy()
                    except:
                        print(f"frame doesn't exist..")

            except Exception as e:
                print(f"{global_use_for_client.FILE_NAME}: Error occurred while waiting for important data:", e)
            time.sleep(5)  # Adjust the delay as needed
        else:
            break


def run_important(data):
    """
    This function processes and displays an important notification regardless of the user's current screen.

    The notification data is a string formatted as "friend:request:stream_id".
    The function splits this string to extract the friend's name, request message, and stream ID.
    It then displays this information in a frame at a specified location on the screen, with options to answer or decline.

    :param data: string. The important notification data formatted as "friend:request:stream_id".
    :return: Nothing.
    """
    global IMPORTANT_FRAME

    friend, request, stream_id = data.split(":")  # Split the data into friend's name and request
    print(f"{global_use_for_client.FILE_NAME}: friend: {friend}, request: {request}, id: {stream_id}")

    IMPORTANT_FRAME = tk.Frame(global_use_for_client.ROOT, bg=global_use_for_client.INCOMING_CALL_COLOR)
    IMPORTANT_FRAME.place(x=global_use_for_client.X_ALIGNMENT + (global_use_for_client.WINDOW_WIDTH -
                                                                 global_use_for_client.X_ALIGNMENT)
                            // 2 - 170, y=global_use_for_client.Y_ALIGNMENT)

    friend_label = tk.Label(IMPORTANT_FRAME, text=friend, fg=global_use_for_client.TEXT_COLOR_BRIGHT,
                            bg=global_use_for_client.INCOMING_CALL_COLOR, font=(global_use_for_client.FONT_STYLE,
                                                                                global_use_for_client.FONT_SIZE))
    friend_label.pack(fill=tk.BOTH, expand=True)
    request_label = tk.Label(IMPORTANT_FRAME, text=request, fg=global_use_for_client.IMPORTANT_REQUEST_COLOR,
                             bg=global_use_for_client.INCOMING_CALL_COLOR, font=(global_use_for_client.FONT_STYLE,
                                                                                 global_use_for_client.FONT_SIZE))
    request_label.pack(fill=tk.BOTH, expand=True)
    decline = customtkinter.CTkImage(light_image=Image.open(fr"{os.getcwd()}\Pictures\decline_call.png"),
                                                    size=(50, 50))
    decline_button = customtkinter.CTkButton(master=IMPORTANT_FRAME, text="", width=50, image=decline,
                                                    command=decline_call, fg_color="transparent",
                                                    hover_color=global_use_for_client.HOVER_COLOR)
    decline_button.pack(side=tk.LEFT)
    answer_partial = partial(answer_call, stream_id)
    answer = customtkinter.CTkImage(light_image=Image.open(fr"{os.getcwd()}\Pictures\answer_call.png"),
                                                    size=(50, 50))
    answer_button = customtkinter.CTkButton(master=IMPORTANT_FRAME, text="", width=50, image=answer,
                                                    command=answer_partial, fg_color="transparent",
                                                    hover_color=global_use_for_client.HOVER_COLOR)
    answer_button.pack(side=tk.RIGHT)


def decline_call():
    """
    This function's purpose is to decline an incoming call by sending a request to the server which would ask
    to clear all important notification from the DB. Once the server processes
    this request, the important notification is cleared on the server side. Consequently, the next time
    the client requests important notifications from the server, the server will respond with 'EMPTY'.
    This 'EMPTY' response will indicate to the client that there are no important notifications, prompting
    the client to remove the IMPORTANT_FRAME.

    :return: Nothing
    """

    print(f"{global_use_for_client.FILE_NAME}: in Declined call")
    message = {"request": "clean important"}
    encryption_decryption.protocol_send_for_client(global_use_for_client.server_socket_backup, message,
                                                   global_use_for_client.MAIN_KEY)


def answer_call(stream_id):
    """
    This function sends a request to the server to join an existing call using the provided stream_id.

    The function notifies the server which call the client wants to join by sending a request containing the stream_id.
    Finally, it destroys the home GUI and initiates the call handler. (with the new GUI)

    :param stream_id: string. The call's special identifier.
    :return: Nothing.
    """
    print(f"{global_use_for_client.FILE_NAME}: in answer call. id={stream_id}")
    global_use_for_client.call_mode = True
    message = {"request": "start call", "id": stream_id}
    encryption_decryption.protocol_send_for_client(global_use_for_client.server_socket, message, global_use_for_client.MAIN_KEY)

    message = {"request": "start call"}
    encryption_decryption.protocol_send_for_client(global_use_for_client.server_socket_backup, message, global_use_for_client.MAIN_KEY)

    global_use_for_client.server_socket.close()
    global_use_for_client.server_socket_backup.close()

    global_use_for_client.ROOT.destroy()
    call_handler.main()


def show_notifications():
    home_structure()
    notifications_display.main()


def show_friends():
    global canvas
    home_structure()
    friends_functionality.main(canvas)


def add_friend():
    home_structure()
    add_friend_display.main()


def create_group():
    global canvas
    home_structure()
    create_group_display.main(canvas)


def show_discover():
    global canvas
    home_structure()  # resetting whatever that was before
    discover_display.main(canvas)


def home_structure():
    """
    This function's purpose is to set the default GUI (for users who already signed in the system)
    :return: Nothing.
    """
    global canvas
    print(f"{global_use_for_client.FILE_NAME}: in home_structure")
    global_use_for_client.MENU_LAYOUTS = []

    flag = True
    if global_use_for_client.ROOT is not None:
        global_use_for_client.reset_root(global_use_for_client.ROOT)  # resetting root layouts
    else:  # doesn't exists yet
        flag = False
        global_use_for_client.ROOT = tk.Tk()

    global_use_for_client.ROOT.title("Home")

    # -----------------------------------------------------------------------------------------------------------
    # Set the border color
    global_use_for_client.ROOT.tk_setPalette(background=global_use_for_client.BACKGROUND_COLOR, foreground="black",
                       activeBackground=global_use_for_client.BACKGROUND_COLOR, activeForeground="black")

    global_use_for_client.ROOT.geometry(f"{global_use_for_client.WINDOW_WIDTH}x{global_use_for_client.WINDOW_HEIGHT - 45}")
    canvas = tk.Canvas(global_use_for_client.ROOT, width=global_use_for_client.WINDOW_WIDTH, height=global_use_for_client.WINDOW_HEIGHT,
                       bg=global_use_for_client.BACKGROUND_COLOR)  # Match root's background
    canvas.pack(fill="both", expand=True)

    # Make a frame for the custom title bar
    title_bar = Frame(canvas, bg=global_use_for_client.BACKGROUND_COLOR, relief='raised', bd=0, highlightthickness=0)

    # Put a close button on the title bar
    close_button = Button(title_bar, text='X', command=global_use_for_client.ROOT.destroy, bg="#2e2e2e", padx=15, pady=3,
                          activebackground='red', bd=0, font="bold", fg='white', highlightthickness=0)

    # Pack the buttons on the title bar
    close_button.pack(side=RIGHT)
    # Pack the title bar at the top
    title_bar.pack(side='top', fill=X)
    # -----------------------------------------------------------------------------------------------------------

    project_name = Image.open(fr"{os.getcwd()}\Pictures\logo.png")
    project_name = project_name.resize((220, 40), Image.LANCZOS)  # Ensure smooth resizing
    project_name_photo = ImageTk.PhotoImage(project_name)

    # Create the label and display the image
    project_name_photo_label = tk.Label(global_use_for_client.ROOT, image=project_name_photo, background=global_use_for_client.BACKGROUND_COLOR)
    project_name_photo_label.photo = project_name_photo  # Reference the PhotoImage to prevent garbage collection
    project_name_photo_label.place(x=10, y=10)

    global_use_for_client.X_ALIGNMENT = project_name.width + 20  # x start of dynamic display part of the window
    global_use_for_client.Y_ALIGNMENT = project_name.height + 20  # y start of dynamic display part of the window.
    canvas.create_line(global_use_for_client.X_ALIGNMENT, 0, global_use_for_client.X_ALIGNMENT, global_use_for_client.WINDOW_HEIGHT, fill=global_use_for_client.LINE_COLOR, width=1)
    canvas.create_line(0, global_use_for_client.Y_ALIGNMENT, global_use_for_client.WINDOW_WIDTH, 61, fill=global_use_for_client.LINE_COLOR, width=1)  # Adjust y-coordinate for desired position

    my_username__ = customtkinter.CTkButton(master=global_use_for_client.ROOT, text=global_use_for_client.center_data(global_use_for_client.my_username, 22), fg_color=global_use_for_client.BACKGROUND_COLOR,
                                            hover_color=global_use_for_client.BACKGROUND_COLOR,
                                            text_color=global_use_for_client.TEXT_COLOR, height=50,
                                            font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE), anchor="w")
    my_username__.pack(padx=3, pady=1)
    my_username__.place(x=0, y=global_use_for_client.WINDOW_HEIGHT - 120)

    add_friends_button_ = customtkinter.CTkButton(master=global_use_for_client.ROOT, text="Add Friend", command=add_friend,
                                                  fg_color=global_use_for_client.ADD_FRIEND_HOVER_COLOR,
                                                  hover_color=global_use_for_client.ADD_FRIEND_HOVER_COLOR,
                                                  text_color=global_use_for_client.TEXT_COLOR_BRIGHT,
                                                  width=160, height=50,
                                                  font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE))
    add_friends_button_.pack(padx=3, pady=1)
    add_friends_button_.place(x=global_use_for_client.WINDOW_WIDTH - 250, y=7)
    global_use_for_client.add_friends_button = add_friends_button_

    select_friends_button_ = customtkinter.CTkButton(master=global_use_for_client.ROOT, text="Select Friends", command=create_group,
                                                     fg_color=global_use_for_client.ADD_FRIEND_HOVER_COLOR,
                                                     hover_color=global_use_for_client.ADD_FRIEND_HOVER_COLOR,
                                                     text_color=global_use_for_client.TEXT_COLOR_BRIGHT,
                                                     width=160, height=50,
                                                     font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE))
    select_friends_button_.pack(padx=3, pady=1)
    select_friends_button_.place(x=int(global_use_for_client.add_friends_button.place_info()['x']) - global_use_for_client.add_friends_button.winfo_reqwidth() - 40, y=7)
    global_use_for_client.select_friends_button = select_friends_button_

    notifications_button = customtkinter.CTkButton(master=global_use_for_client.ROOT, text="Notifications", command=show_notifications,
                                                   fg_color="transparent", hover_color=global_use_for_client.HOVER_COLOR,
                                                   text_color=global_use_for_client.TEXT_COLOR,
                                                   width=global_use_for_client.X_ALIGNMENT, height=45,
                                                   font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE))
    notifications_button.pack(padx=3, pady=1)
    notifications_button.place(x=0, y=62)

    friends_button = customtkinter.CTkButton(master=global_use_for_client.ROOT, text="Friends", command=show_friends, fg_color="transparent"
                                             , hover_color=global_use_for_client.HOVER_COLOR, text_color=global_use_for_client.TEXT_COLOR,
                                             width=global_use_for_client.X_ALIGNMENT, height=45,
                                             font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE))
    friends_button.pack(padx=3, pady=1)
    friends_button.place(x=0, y=109)

    discover_button = customtkinter.CTkButton(master=global_use_for_client.ROOT, text="Discover", command=show_discover,
                                              fg_color="transparent"
                                              , hover_color=global_use_for_client.HOVER_COLOR, text_color=global_use_for_client.TEXT_COLOR,
                                              width=global_use_for_client.X_ALIGNMENT, height=45,
                                              font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE))
    discover_button.pack(padx=3, pady=1)
    discover_button.place(x=0, y=156)

    global_use_for_client.MENU_LAYOUTS.extend([title_bar, project_name_photo_label, my_username__, notifications_button, friends_button, discover_button,
                                               global_use_for_client.add_friends_button, global_use_for_client.select_friends_button])

    global_use_for_client.X_ALIGNMENT += 10
    global_use_for_client.Y_ALIGNMENT += 40
    if flag is False:
        global_use_for_client.ROOT.mainloop()


def main():
    # Start a thread to constantly run the wait_for_important function
    important_thread = threading.Thread(target=wait_for_important, daemon=True)
    important_thread.start()

    home_structure()


def TESTING(user):
    """
    This function is skipping the login page. FOR TESTING ONLY.
    :return:
    """

    if global_use_for_client.server_socket is None:

        global_use_for_client.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        global_use_for_client.server_socket.connect((global_use_for_client.IP_TO_CONNECT, global_use_for_client.PORT_TO_CONNECT))

        global_use_for_client.server_socket_backup = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        global_use_for_client.server_socket_backup.connect((global_use_for_client.IP_TO_CONNECT, global_use_for_client.PORT_TO_CONNECT))  # connecting another backup socket
        global_use_for_client.my_username = user

        print(f"{global_use_for_client.FILE_NAME}: connection has been made with the server!")
        global_use_for_client.MAIN_KEY = encryption_decryption.handle_keys_exchange_for_client(global_use_for_client.server_socket)
        print(f"\n{global_use_for_client.FILE_NAME}: server_socket1 is {global_use_for_client.server_socket}\nserver_socket2 is {global_use_for_client.server_socket_backup}\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")

        message = {"request": "set username", "username": user}
        encryption_decryption.protocol_send_for_client(global_use_for_client.server_socket, message, global_use_for_client.MAIN_KEY)


def FOR_TESTING(user, name="[HOME]"):
    global_use_for_client.FILE_NAME = name
    TESTING(user)
    main()


if __name__ == "__main__":
    FOR_TESTING(user="lirazshimon11")
