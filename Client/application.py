# IMPORTS:
import re
import socket
import threading
from tkinter import *
from PIL import Image, ImageTk
import tkinter as tk
import os
import register  # python file
import home      # python file
import customtkinter
import encryption_decryption
import global_use_for_client
import time

# Globals:
global entry_username, entry_password

entry_code = None
# title_bar_thread = None
# Set appearance mode and default color theme
customtkinter.set_appearance_mode("System")
flag = True


def validate_credentials(username, password):
    """
    This function checks if the username and password contain only alphanumeric characters.

    :param username: str. The username to be validated.
    :param password: str. The password to be validated.
    :return: bool. True if both username and password are valid, False otherwise.
    """
    # Regular expression to match alphanumeric characters
    regex = re.compile('^[a-zA-Z0-9]+$')

    # Check if username and password match the regex
    if regex.match(username) and regex.match(password):
        return True
    else:
        return False


def go_to_register(event=None):
    """
    This function directs the code execution to the register module.

    :param event: Event, optional. An event object (default is None).
    :return: Nothing.
    """
    register.main()


def show_time():
    """
    This function displays a countdown timer on the screen.

    This function receives the time remaining from the server and updates the UI
    to display the countdown. The timer color changes to indicate urgency as it
    approaches zero.

    :return: Nothing.
    """
    global flag
    dynamic_color = global_use_for_client.ADD_FRIEND_HOVER_COLOR
    if global_use_for_client.time_label:  # destroying the previous label.
        global_use_for_client.time_label.destroy()
    global_use_for_client.time_label = customtkinter.CTkLabel(master=global_use_for_client.ROOT, corner_radius=10, text="sending...",
                                                              font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE_SMALL),
                                                              text_color=dynamic_color)
    global_use_for_client.time_label.place(x=global_use_for_client.WINDOW_WIDTH / 2 + 60, y=400)

    email_sent = encryption_decryption.receive_message(global_use_for_client.server_socket, global_use_for_client.MAIN_KEY)
    if "sent" in email_sent.lower():
        message = {"request": "time"}
        encryption_decryption.protocol_send_for_client(global_use_for_client.server_socket_backup, message,
                                                       global_use_for_client.MAIN_KEY)
        time_remain = int(encryption_decryption.receive_message(global_use_for_client.server_socket_backup,
                                                     global_use_for_client.MAIN_KEY))
        print(f"remaining time --> {time_remain}")
        while flag:
            if global_use_for_client.time_label:  # destroying the previous label.
                global_use_for_client.time_label.destroy()
            global_use_for_client.time_label = customtkinter.CTkLabel(master=global_use_for_client.ROOT,
                                                                      corner_radius=20, text=time_remain,
                                                                      font=(global_use_for_client.FONT_STYLE,
                                                                            global_use_for_client.FONT_SIZE),
                                                                      text_color=dynamic_color)
            global_use_for_client.time_label.place(x=global_use_for_client.WINDOW_WIDTH / 2 + 60, y=400)
            time.sleep(1)

            time_remain -= 1
            if time_remain < 6:
                dynamic_color = global_use_for_client.ERROR_COLOR

            if time_remain == 0:
                print(f"Time is up!")
                break

        if time_remain == 0:
            application_structure()


def code_structure():
    """
    This function sets up the UI structure for entering the authorization code.

    This function resets the root window and adds the necessary components
    for the user to enter an authorization code.

    :return: Nothing.
    """
    global entry_code
    global_use_for_client.reset_root(global_use_for_client.ROOT)
    # if global_use_for_client.ROOT:
    #     for widget in global_use_for_client.ROOT.winfo_children():
    #         widget.destroy()
    project_name = Image.open(fr"{os.getcwd()}\Pictures\logo.png")
    project_name_photo = ImageTk.PhotoImage(project_name)
    project_name_photo_label = tk.Label(global_use_for_client.ROOT, image=project_name_photo,
                                        background=global_use_for_client.BACKGROUND_COLOR)
    project_name_photo_label.photo = project_name_photo

    entry_code = customtkinter.CTkEntry(master=global_use_for_client.ROOT, corner_radius=20, width=400, placeholder_text="Code",
                                        height=40, font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE),
                                        validate="key",
                                        validatecommand=(global_use_for_client.ROOT.register(lambda text: 0 <= len(text) <= 6), "%P"))
    send = customtkinter.CTkButton(master=global_use_for_client.ROOT, fg_color=global_use_for_client.COLOR, hover_color=global_use_for_client.HOVER_COLOR,
                                   text="Send Code!",
                                   corner_radius=6, command=login_verification, width=180, height=50,
                                   text_color=global_use_for_client.TEXT_COLOR,
                                   font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE))
    entry_code.bind("<Return>", lambda event: login_verification)

    project_name_photo_label.place(x=global_use_for_client.WINDOW_WIDTH / 2 - 280, y=100)
    entry_code.place(x=global_use_for_client.WINDOW_WIDTH / 2 - 220, y=300)
    send.place(x=global_use_for_client.WINDOW_WIDTH / 2 - 120, y=370)


def login_verification():
    """
    This function verifies the authorization code entered by the user.

    This function sends the authorization code to the server and checks the response
    to determine if the user is authorized. If authorized, it transitions to the home module.

    :return: Nothing.
    """
    print(global_use_for_client.my_username)
    global entry_code, flag
    encryption_decryption.protocol_send_for_server(global_use_for_client.server_socket, entry_code.get(), global_use_for_client.MAIN_KEY)
    answer = encryption_decryption.receive_message(global_use_for_client.server_socket, global_use_for_client.MAIN_KEY)
    print(f"[APPLICATION]: answer is {answer.lower()}")
    if "authorized" in answer.lower():
        flag = False  # stop receiving time..
        home.main()
    else:
        display_try_again_message(global_use_for_client.INCORRECT_INFO, global_use_for_client.WINDOW_WIDTH / 2 - 130, 440)


def login(event=None):  # Accept an event argument to handle Enter key press
    """
    This function handles the login process for the user.

    This function validates the username and password, sends the login request to the server,
    and handles the server's response to determine if further steps (like entering an authorization code) are needed.

    :param event: Event, optional. An event object (default is None).
    :return: Nothing.
    """
    print("in login")
    global entry_username, entry_password
    message = {"request": "login", "username": entry_username.get(), "password": entry_password.get()}
    if validate_credentials(message["username"], message["password"]):
        encryption_decryption.protocol_send_for_client(global_use_for_client.server_socket, message, global_use_for_client.MAIN_KEY)  # sending --> request and all he needs to
        decrypted_msg = encryption_decryption.receive_message(global_use_for_client.server_socket, global_use_for_client.MAIN_KEY)
        print(f"[APPLICATION]: answer is {decrypted_msg}")

        if "code" in decrypted_msg.lower():  # authorization code is needed.
            global_use_for_client.my_username = message["username"]
            print(f"[APPLICATION]: should stop going to title_bar_display.py")
            threading.Thread(target=show_time, ).start()
            code_structure()
        else:
            display_try_again_message(global_use_for_client.INCORRECT_INFO, global_use_for_client.WINDOW_WIDTH / 2 + 60, 450)
    else:  # the input is invalid - no need to bother the server.
        print("invalid credentials.")
        display_try_again_message(global_use_for_client.INVALID_INFO, global_use_for_client.WINDOW_WIDTH / 2 + 60, 450)


def display_try_again_message(text, x, y):
    """
    This function displays a 'Try again' message on the screen.

    This function creates a message label and places it at the specified coordinates.
    The message is automatically removed after 3 seconds.

    :param text: str. The message text to be displayed.
    :param x: int. The x-coordinate for the message placement.
    :param y: int. The y-coordinate for the message placement.
    :return: Nothing.
    """
    # Display "Try again" message
    try_again_label = customtkinter.CTkButton(master=global_use_for_client.ROOT,
                                              text=text,
                                              text_color=global_use_for_client.TEXT_COLOR_BRIGHT,
                                              fg_color=global_use_for_client.ERROR_COLOR, corner_radius=500,
                                              hover_color=global_use_for_client.ERROR_COLOR, height=15)
    try_again_label.place(x=x, y=y)  # Place the label at appropriate position

    global_use_for_client.ROOT.after(3000, try_again_label.destroy)


def focus_password_entry(event):
    """
    This function sets focus to the password entry field.

    :param event: Event. The event object triggering this function.
    :return: None.
    """
    entry_password.focus_set()


def connectToServer():
    """
    This function establishes a connection to the server.

    This function creates and connects the primary and backup sockets to the server,
    and handles the key exchange process.

    :return: Nothing.
    """
    print(f"[APPLICATION]: in connect to server.")
    if global_use_for_client.server_socket is None:

        global_use_for_client.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        global_use_for_client.server_socket.connect((global_use_for_client.IP_TO_CONNECT, global_use_for_client.PORT_TO_CONNECT))

        global_use_for_client.server_socket_backup = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        global_use_for_client.server_socket_backup.connect((global_use_for_client.IP_TO_CONNECT, global_use_for_client.PORT_TO_CONNECT))  # connecting another backup socket

        print(f"{global_use_for_client.FILE_NAME}: connection has been made with the server!")
        global_use_for_client.MAIN_KEY = encryption_decryption.handle_keys_exchange_for_client(global_use_for_client.server_socket)
        print(f"\n{global_use_for_client.FILE_NAME}: server_socket1 is {global_use_for_client.server_socket}\nserver_socket2 is {global_use_for_client.server_socket_backup}\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")


def application_structure():
    """
    This function sets up the UI structure for the login screen.

    This function resets the root window and adds the necessary components
    for the user to enter their username and password.

    :return: Nothing.
    """
    global entry_username, entry_password
    print(f"[APPLICATION]: in application_structure! username={global_use_for_client.my_username}. server_socket={global_use_for_client.server_socket}")
    flag = True
    if global_use_for_client.ROOT is not None:
        global_use_for_client.reset_root(global_use_for_client.ROOT)  # clearing the previous root.
    else:  # doesn't exists yet
        flag = False
        global_use_for_client.ROOT = tk.Tk()

    global_use_for_client.ROOT.title("Application")

    # -----------------------------------------------------------------------------------------------------------
    # Set the border color
    global_use_for_client.ROOT.tk_setPalette(background=global_use_for_client.BACKGROUND_COLOR, foreground="black",
                                             activeBackground=global_use_for_client.BACKGROUND_COLOR,
                                             activeForeground="black")

    global_use_for_client.ROOT.geometry(
        f"{global_use_for_client.WINDOW_WIDTH}x{global_use_for_client.WINDOW_HEIGHT - 45}")
    canvas = tk.Canvas(global_use_for_client.ROOT, width=global_use_for_client.WINDOW_WIDTH,
                       height=global_use_for_client.WINDOW_HEIGHT,
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

    # Load image
    project_name = Image.open(fr"{os.getcwd()}\Pictures\logo.png")
    project_name_photo = ImageTk.PhotoImage(project_name)
    project_name_photo_label = tk.Label(global_use_for_client.ROOT, image=project_name_photo, background=global_use_for_client.BACKGROUND_COLOR)
    project_name_photo_label.photo = project_name_photo
    project_name_photo_label.place(x=global_use_for_client.WINDOW_WIDTH / 2 - 280, y=100)

    # username entry:
    entry_username = customtkinter.CTkEntry(master=global_use_for_client.ROOT, corner_radius=20, width=400, placeholder_text="Username",
                                            height=40, font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE), validate="key",
                                            validatecommand=(global_use_for_client.ROOT.register(lambda text: len(text) <= global_use_for_client.MAX_CHARACTERS_AMOUNT), "%P"))

    # password entry:
    entry_password = customtkinter.CTkEntry(master=global_use_for_client.ROOT, corner_radius=20, width=400, show="*",
                                            placeholder_text="Password", height=40,
                                            font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE), validate="key",
                                            validatecommand=(global_use_for_client.ROOT.register(lambda text: len(text) <= global_use_for_client.MAX_CHARACTERS_AMOUNT), "%P"))

    login_button = customtkinter.CTkButton(master=global_use_for_client.ROOT, fg_color=global_use_for_client.COLOR, hover_color=global_use_for_client.HOVER_COLOR,
                                           text="Login",
                                           corner_radius=6, command=login, width=180, height=50,
                                           text_color=global_use_for_client.TEXT_COLOR,
                                           font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE))
    sign_up_button = customtkinter.CTkButton(master=global_use_for_client.ROOT, fg_color=global_use_for_client.COLOR, hover_color=global_use_for_client.HOVER_COLOR,
                                             text="Sign Up",
                                             corner_radius=6, command=go_to_register, width=80, height=10,
                                             text_color=global_use_for_client.TEXT_COLOR,
                                             font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE))

    entry_username.bind("<Return>", focus_password_entry)
    entry_password.bind("<Return>", login)

    entry_username.place(x=global_use_for_client.WINDOW_WIDTH / 2 - 220, y=300)
    entry_password.place(x=global_use_for_client.WINDOW_WIDTH / 2 - 220, y=350)
    login_button.place(x=global_use_for_client.WINDOW_WIDTH / 2 - 120, y=420)
    sign_up_button.place(x=global_use_for_client.WINDOW_WIDTH / 2 - 120, y=480)

    if flag is False:
        global_use_for_client.ROOT.mainloop()


def main():
    """
    This function runs the connecting function and the login structure.

    :return: Nothing.
    """
    global entry_username, entry_password
    # global flag
    connectToServer()
    # # updating important variables:
    # if socket1 and socket2 and KEY and name:
    #     (global_use_for_client.server_socket, global_use_for_client.server_socket_backup, global_use_for_client.MAIN_KEY,
    #     global_use_for_client.my_username, global_use_for_client.FILE_NAME) = socket1, socket2, KEY, user, name
    application_structure()


if __name__ == "__main__":
    main()
