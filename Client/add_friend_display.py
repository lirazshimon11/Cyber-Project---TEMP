import customtkinter
import encryption_decryption
import tkinter as tk
import global_use_for_client

# GLOBALS:
request_entry = None


def main():
    """
    This function initializes and sets up the 'Add Friend' UI components.

    This function sets up the input field for entering a friend's username
    and the button to send the friend request. It also binds the Enter key
    to the follow_request function.
    :return: Nothing.
    """
    # UPDATING GLOBAL VALUES FOR THE FUNCTION- follow_request
    global request_entry

    request_entry = customtkinter.CTkEntry(master=global_use_for_client.ROOT, font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE_SMALL),
                                           corner_radius=10, width=1200, height=40, placeholder_text="Please type your friend's username here..", validate="key",
                                           validatecommand=(global_use_for_client.ROOT.register(lambda text: len(text) <= global_use_for_client.MAX_CHARACTERS_AMOUNT), "%P"))
    request_entry.place(x=global_use_for_client.X_ALIGNMENT + 10, y=65)

    request_button = customtkinter.CTkButton(master=global_use_for_client.ROOT, bg_color=global_use_for_client.BACKGROUND_COLOR, fg_color=global_use_for_client.SEND_REQUEST_COLOR,
                                             hover_color=global_use_for_client.HOVER_COLOR, text="send request", corner_radius=10,
                                             command=follow_request, width=40, font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE_SMALL-1))
    request_entry.bind("<Return>", lambda e: follow_request)

    request_button.place(x=global_use_for_client.X_ALIGNMENT + request_entry["width"] - request_button["width"] - 82, y=70)


def follow_request():
    """
    This function handles the process of sending a friend request.

    This function retrieves the username from the entry field and sends a
    friend request to the server. It updates the UI to display the status
    of the request. If the username is the same as the current user's, it
    displays an error message without sending the request to the server.
    """
    print(f"[HOME] in follow_request")
    global request_entry
    if request_entry.get() != global_use_for_client.my_username:  # Filter
        message = {"request": "friendship request", "username": request_entry.get()}  # username is the future friend

        encryption_decryption.protocol_send_for_client(global_use_for_client.server_socket, message, global_use_for_client.MAIN_KEY)  # sending --> request and all he needs to
        response = encryption_decryption.receive_message(global_use_for_client.server_socket, global_use_for_client.MAIN_KEY)
        text_c = "#B3575B"
        x = int(request_entry.place_info()['x']) + request_entry["width"] - 425
        print(f"x={x}")
        if "!" in response:  # sent successfully
            text_c = "#30BD4A"
            x += 370
        status_label = tk.Label(global_use_for_client.ROOT, text=response, bg=global_use_for_client.BACKGROUND_COLOR, fg=text_c, padx=1, pady=1, font=(global_use_for_client.FONT_STYLE, 11))
        status_label.pack()
        status_label.place(x=x, y=110)  # Adjust the position as needed

        # Schedule the removal of the status message after 2 seconds
        global_use_for_client.ROOT.after(2000, lambda: [status_label.destroy()])
    else:  # no need to send the server, this is wrong anyway.
        text_c = "#B3575B"
        x = int(request_entry.place_info()['x']) + request_entry["width"] - 425
        status_label = tk.Label(global_use_for_client.ROOT, text=global_use_for_client.INCORRECT_INFO2, bg=global_use_for_client.BACKGROUND_COLOR,
                                fg=text_c, padx=1, pady=1, font=(global_use_for_client.FONT_STYLE, 11))
        status_label.pack()
        status_label.place(x=x, y=110)  # Adjust the position as needed

        # Schedule the removal of the status message after 2 seconds
        global_use_for_client.ROOT.after(2000, lambda: [status_label.destroy()])