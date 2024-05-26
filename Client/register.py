import os
import tkinter as tk
from tkinter import *
import customtkinter
from PIL import Image, ImageTk, ImageSequence
import application
import encryption_decryption
import global_use_for_client


# GLOBALS:
global client_socket
global entry_full_name, entry_email, entry_username, entry_password, entry_phone_number
# flag = True


def sign_up():
    """
    This function's purpose is to check if all the information the user typed is the correct information.
    This function will communicate with the server and check the receiving data
    :param event: None
    :return: Nothing.
    """
    global entry_full_name, entry_email, entry_username, entry_password, entry_phone_number, register

    message = {"request": "register", "full_name": entry_full_name.get(), "email": entry_email.get(),
               "username": entry_username.get(), "password": entry_password.get(), "phone_number": entry_phone_number.get()}
    print(message)
    encryption_decryption.protocol_send_for_client(global_use_for_client.server_socket, message, global_use_for_client.MAIN_KEY)  # sending --> request and all he needs to

    decrypted_msg = encryption_decryption.receive_message(global_use_for_client.server_socket, global_use_for_client.MAIN_KEY)  # receiving --> decrypted YES/NO.
    print(f"[APPLICATION]: answer is {decrypted_msg}")
    if decrypted_msg == "YES":
        # flag = False
        application.application_structure()  # For some reason I should give the show function the main key back.
    else:
        print("there's a problem.")


def focus_email_entry():
    entry_email.focus_set()


def focus_username_entry():
    entry_username.focus_set()


def focus_password_entry():
    entry_password.focus_set()


def focus_phone_number_entry():
    entry_phone_number.focus_set()


def main():
    global entry_full_name, entry_email, entry_username, entry_password, entry_phone_number

    flag = True
    if global_use_for_client.ROOT is not None:
        global_use_for_client.reset_root(global_use_for_client.ROOT)  # clearing the previous root.
    else:  # doesn't exists yet
        flag = False
        global_use_for_client.ROOT = tk.Tk()

    global_use_for_client.ROOT.title("register")

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

    # Load image
    project_name = Image.open(fr"{os.getcwd()}\Pictures\logo.png")
    project_name_photo = ImageTk.PhotoImage(project_name)
    project_name_photo_label = tk.Label(global_use_for_client.ROOT, image=project_name_photo, background=global_use_for_client.BACKGROUND_COLOR)
    project_name_photo_label.photo = project_name_photo
    project_name_photo_label.place(x=global_use_for_client.WINDOW_WIDTH / 2 - 296, y=100)

    entry_full_name = customtkinter.CTkEntry(master=global_use_for_client.ROOT, corner_radius=20, width=400, placeholder_text="Full Name", validate="key",
                                             validatecommand=(global_use_for_client.ROOT.register(lambda text: len(text) <= global_use_for_client.MAX_CHARACTERS_AMOUNT), "%P"))
    entry_email = customtkinter.CTkEntry(master=global_use_for_client.ROOT, corner_radius=20, width=400, placeholder_text="Email", validate="key",
                                         validatecommand=(global_use_for_client.ROOT.register(lambda text: len(text) <= global_use_for_client.MAX_CHARACTERS_AMOUNT), "%P"))
    entry_username = customtkinter.CTkEntry(master=global_use_for_client.ROOT, corner_radius=20, width=400, placeholder_text="Username", validate="key",
                                            validatecommand=(global_use_for_client.ROOT.register(lambda text: len(text) <= global_use_for_client.MAX_CHARACTERS_AMOUNT), "%P"))
    entry_password = customtkinter.CTkEntry(master=global_use_for_client.ROOT, corner_radius=20, width=400, show="*", placeholder_text="Password", validate="key",
                                            validatecommand=(global_use_for_client.ROOT.register(lambda text: len(text) <= global_use_for_client.MAX_CHARACTERS_AMOUNT), "%P"))
    entry_phone_number = customtkinter.CTkEntry(master=global_use_for_client.ROOT, corner_radius=20, width=400, placeholder_text="Phone Number", validate="key",
                                                validatecommand=(global_use_for_client.ROOT.register(lambda text: len(text) <= global_use_for_client.MAX_CHARACTERS_AMOUNT), "%P"))

    submit_button = customtkinter.CTkButton(master=global_use_for_client.ROOT, fg_color=global_use_for_client.COLOR, hover_color=global_use_for_client.HOVER_COLOR, text="SUBMIT",
                                            corner_radius=6, command=sign_up, text_color=global_use_for_client.TEXT_COLOR, font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE))

    entry_full_name.bind("<Return>", lambda e: focus_email_entry())
    entry_email.bind("<Return>", lambda e: focus_username_entry())
    entry_username.bind("<Return>", lambda e: focus_password_entry())
    entry_password.bind("<Return>", lambda e: focus_phone_number_entry())
    entry_phone_number.bind("<Return>", lambda e: sign_up())

    entry_full_name.place(x=global_use_for_client.WINDOW_WIDTH / 2 - 220, y=300)
    entry_email.place(x=global_use_for_client.WINDOW_WIDTH / 2 - 220, y=350)
    entry_username.place(x=global_use_for_client.WINDOW_WIDTH / 2 - 220, y=400)
    entry_password.place(x=global_use_for_client.WINDOW_WIDTH / 2 - 220, y=450)
    entry_phone_number.place(x=global_use_for_client.WINDOW_WIDTH / 2 - 220, y=500)
    submit_button.place(x=(global_use_for_client.WINDOW_WIDTH - 200) / 2, y=600)

    if flag is False:
        global_use_for_client.ROOT.mainloop()


if __name__ == "__main__":
    main()