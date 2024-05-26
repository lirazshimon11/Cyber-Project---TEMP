import tkinter
import customtkinter
import encryption_decryption
import global_use_for_client
global canvas, chat_update_thread
# GLOBALS:
request_entry = None
checkboxes = []


def main(canvas_):
    """
    This function's purpose is to display friends and create a group.

    This function sets up the GUI for displaying the user's friends and providing an option to create a group.
    It sends a request to the server to get the list of friends and displays them as checkboxes. The user can
    select friends to include in a new group.

    :param canvas_: The tkinter canvas on which the UI elements will be placed.
    :return: Nothing.
    """
    global canvas, chat_update_thread, checkboxes

    canvas = canvas_

    create_group_button = customtkinter.CTkButton(master=global_use_for_client.ROOT, text="Create Group", command=send_chosen_friends,
                                                  fg_color=global_use_for_client.ADD_FRIEND_HOVER_COLOR,
                                                  hover_color=global_use_for_client.SEND_REQUEST_COLOR,
                                                  text_color=global_use_for_client.TEXT_COLOR_BRIGHT,
                                                  width=160, height=50, font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE))
    create_group_button.pack(padx=3, pady=1)
    create_group_button.place(x=global_use_for_client.X_ALIGNMENT, y=7)
    # home.to_be_forgotten.append(create_group_button)
    print("in show friends")
    message = {"request": "get friends"}
    encryption_decryption.protocol_send_for_client(global_use_for_client.server_socket, message, global_use_for_client.MAIN_KEY)  # sending --> request and all he needs to

    response = encryption_decryption.receive_message(global_use_for_client.server_socket, global_use_for_client.MAIN_KEY)  # receiving --> response to my request
    y = 62
    if "EMPTY" not in response:
        response_to_array = response.split("\n")
        print(f"[FRIENDS_FUNCTIONALITY]: friends are {response_to_array}")

        for friend in response_to_array:
            if "," not in friend:  # to *avoid* groups.
                check_var = tkinter.StringVar()
                check_var.set("off")

                friend_button = customtkinter.CTkCheckBox(master=global_use_for_client.ROOT, text=friend, corner_radius=10, height=50,
                                                          text_color=global_use_for_client.TEXT_COLOR, onvalue="on", offvalue="off",
                                                          font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE), variable=check_var,
                                                          width=333, fg_color=global_use_for_client.SEND_REQUEST_COLOR, )
                HOVER = global_use_for_client.SEND_REQUEST_COLOR
                friend_button.configure(hover_color=HOVER)
                friend_button.place(x=global_use_for_client.X_ALIGNMENT, y=y)
                friend_button.var = check_var
                checkboxes.append(friend_button)

                y += friend_button.winfo_height() + 55

                # home.to_be_forgotten.append(friend_button)

    else:  # FRIENDS BOX IS EMPTY
        friend_button = customtkinter.CTkButton(master=global_use_for_client.ROOT, text=response, fg_color="transparent", corner_radius=10,
                                                height=50, text_color=global_use_for_client.TEXT_COLOR, font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE),
                                                width=canvas.winfo_screenwidth() - 333, anchor="w")
        HOVER = global_use_for_client.BACKGROUND_COLOR
        friend_button.configure(hover_color=HOVER)
        friend_button.pack()
        friend_button.place(x=global_use_for_client.X_ALIGNMENT, y=y)


def send_chosen_friends():
    """
    This function's purpose is to send the selected friends to the server to create a group.

    This function gathers the friends selected by the user, filters out duplicates, and sends a request to the
    server to create a group with the chosen friends.

    :return: Nothing.
    """
    global checkboxes
    chosen_friends = [global_use_for_client.my_username]
    for checkbox in checkboxes:
        checkbox_value = checkbox.var.get()
        if checkbox_value == "on":
            chosen_friends.append(checkbox.cget("text"))
            print(f"[CREATE_GROUP_DISPLAY]: -----> {chosen_friends}")
    checkboxes = []
    chosen_friends = filter_group(chosen_friends)
    print(f"[CREATE_GROUP_DISPLAY]: chosen friends are: {chosen_friends}")
    if len(chosen_friends) > 1:
        message = {"request": "create group", "group": chosen_friends}
        encryption_decryption.protocol_send_for_client(global_use_for_client.server_socket, message, global_use_for_client.MAIN_KEY)  # sending --> request and all he needs to
    else:  # this isn't a group. not necessary to disturb the server for it..
        pass


def filter_group(group):
    """
    This function's purpose is to search for issues inside the group array and fix them.
    :param group: array.
    :return: the corrected group array.
    """
    res = []
    for username in group:
        if username not in res:
            res.append(username)
    return res