import customtkinter
import encryption_decryption
import global_use_for_client
import friends_functionality


def main(canvas):
    """
    This function's purpose is to display the Discover page.

    This function sets up the GUI for the Discover page, where users can click a button to talk to new people.
    The button is placed on the provided canvas.

    :param canvas: The tkinter canvas on which the UI elements will be placed.
    :return: Nothing.
    """
    print(f"[HOME]: in show_discover")

    global_chat_button = customtkinter.CTkButton(master=global_use_for_client.ROOT, text="Talk To New People", fg_color="transparent", corner_radius=10,
                                                 height=50, text_color=global_use_for_client.TEXT_COLOR, font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE),
                                                 width=canvas.winfo_screenwidth()-333, anchor="w",
                                                 hover_color=global_use_for_client.HOVER_COLOR, command=open_global_chat)

    global_chat_button.pack(padx=3, pady=1)
    global_chat_button.place(x=global_use_for_client.X_ALIGNMENT + 10, y=62)


def open_global_chat():
    """
    This function's purpose is to open the global chat.

    This function sends a request to the server to get all usernames from the database, receives the response,
    and then calls the `open_chat` function from the friends_functionality module with the received usernames.

    :return: Nothing.
    """
    message = {"request": "get usernames"}
    encryption_decryption.protocol_send_for_client(global_use_for_client.server_socket, message, global_use_for_client.MAIN_KEY)  # sending --> request and all he needs to

    response = encryption_decryption.receive_message(global_use_for_client.server_socket, global_use_for_client.MAIN_KEY)  # receiving --> all usernames from the DB.
    print(f"response --> {response}")
    friends_functionality.open_chat(response)



if __name__ == '__main__':
    main()