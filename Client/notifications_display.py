import encryption_decryption
import customtkinter
from functools import partial
import global_use_for_client


def main():

    print(f"[NOTIFICATIONS DISPLAY]: in show notifications. server_socket={global_use_for_client.server_socket}, username is {global_use_for_client.my_username}")
    message = {"request": "get notifications"}
    encryption_decryption.protocol_send_for_client(global_use_for_client.server_socket, message, global_use_for_client.MAIN_KEY)  # sending --> request and all he needs to

    # server_socket.send(encryption_decryption.encrypt_msg_for_client(message, MAIN_KEY))
    response = encryption_decryption.receive_message(global_use_for_client.server_socket, global_use_for_client.MAIN_KEY)
    print(f"[HOME]: your notifications are: {response}")
    try:
        response_to_array = response.split("\n")
        print(f"[HOME]: array of response: {response_to_array}")
        y = 70
        line_y = 106
        for notification in response_to_array:
            print(f"[HOME]: about to create the notification- {notification}")
            notification_ = customtkinter.CTkButton(master=global_use_for_client.ROOT, text=notification, fg_color="transparent",
                                                    corner_radius=10,
                                                    text_color=global_use_for_client.TEXT_COLOR, font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE),
                                                    hover_color=global_use_for_client.BACKGROUND_COLOR)
            notification_.pack()
            notification_.place(x=global_use_for_client.X_ALIGNMENT + 10, y=y)

            if "requested to follow you" in notification:
                friend = notification.split(" ")[0]
                print(f"[HOME] about create accept button for {friend}")

                # Create a closure to capture the current value of friend
                send_response_partial = partial(send_response, friend=friend)

                follow = customtkinter.CTkButton(master=global_use_for_client.ROOT, bg_color="transparent", fg_color="#30BD4A",
                                                 text="Follow", corner_radius=10,
                                                 command=send_response_partial, width=40)

                follow.pack()
                follow.place(x=900, y=y)

            y += 30
            line_y += 43
    except Exception as e:
        print(f"[NOTIFICATIONS DISPLAY]: error --> {e}")


def send_response(friend):
    print(f"in send_response, this function accepts {friend}")
    message = {"request": "accept friend", "username": friend}
    encryption_decryption.protocol_send_for_client(global_use_for_client.server_socket, message, global_use_for_client.MAIN_KEY)  # sending --> request and all he needs to


if __name__ == "__main__":
    main()
