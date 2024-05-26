# this file is responsible for handling video and voice chat with another user.
import datetime
import os
import socket
import threading
import time
import tkinter as tk
from functools import partial
import pyaudio
from PIL import Image, ImageTk, ImageGrab
import customtkinter
import cv2
import global_use_for_client
import numpy as np
import pyautogui
import re

# GLOBALS:
global root_call, FRAME_SIZE, button_video, button_share_screen, button_voice, button_external_control

FRAME_SIZE = (500, 350)
button_video = None
active_streams = {}  # Dictionary to store active streams and their positions
user_positions = {}
user_display_status = {}  # for example: {"lirazshimon11": True, "oran": False}. True - video, False - username


def init_video(camera_number: int):
    """
    This function initializes the video capture for the specified camera number.
    :param camera_number: int
    :return: VideoCapture object or None
    """
    CAP = cv2.VideoCapture(camera_number, cv2.CAP_DSHOW)
    if not CAP.isOpened():
        global button_video
        print("Error: Could not open camera.")
        return None
    return CAP


def init_voice_self():
    """
    This function is initializing the stream to take my own voice stream.
    :return: audio and stream
    """
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        input=True,
                        frames_per_buffer=global_use_for_client.CHUNK)
    print("* Recording")
    return audio, stream


def init_voice_out():
    """
    This function is initializing a stream for taking a data and making a sound out of him.
    :return: audio and stream
    """
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=44100,
                        output=True)
    return audio, stream


def get_video():
    """
    This function captures a video frame from the global video capture object.
    :return: captured frame or None
    """
    print(f"global_use_for_client.CAP is --> {global_use_for_client.CAP}")
    ret, frame = global_use_for_client.CAP.read()
    if not ret:
        print("Error: Failed to capture frame.")
        return None
    # print(f"my frame--> {frame}")
    return frame


def get_voice(stream):
    """
    This function reads a chunk of audio data from the provided stream.
    :param stream: Stream object
    :return: audio data
    """
    data = stream.read(global_use_for_client.CHUNK)
    return data


def get_share_screen():
    """
    This function captures the screen and returns it as an image.
    :return: captured screen image
    """
    screen = pyautogui.screenshot()
    screen_share = np.array(screen)
    screen_share = cv2.cvtColor(screen_share, cv2.COLOR_BGR2RGB)
    screen_share = cv2.resize(screen_share, (global_use_for_client.WINDOW_WIDTH, global_use_for_client.WINDOW_HEIGHT),
                       interpolation=cv2.INTER_AREA)
    return screen_share


def filter_real_username(username):
    """
    This function checks the username to see if it looks okay. If not, return False.
    :param username: string
    :return: bool
    """
    # Check if the username length exceeds the maximum allowed characters
    if len(username) > global_use_for_client.MAX_CHARACTERS_AMOUNT:
        return False

    # Check if the username is just numbers
    if username.isdigit():
        return False

    # Check if the username contains only alphanumeric characters, underscores, and allowed special characters
    if not re.match("^[a-zA-Z0-9_!@#$%^&*~.`]+$", username):
        return False

    # Count the occurrences of special characters from the provided list
    special_list = ['!', '@', '#', '$', '%', '^', '&', '*', '~', '.`']
    special_char_count = sum(1 for char in username if char in special_list)

    # Allow maximum 2 special characters
    if special_char_count > 2:
        return False

    # Additional checks if needed

    return True


def stream_show(username, frame=None, position=None):
    """
    This function displays the video frame or username on the screen.
    :param username: string
    :param frame: image frame (optional)
    :param position: tuple containing x and y coordinates (optional)
    :return: Nothing.
    """
    global root_call, FRAME_SIZE, user_display_status

    if frame is None:
        print("No")
    else:
        print(f"frame exist is {frame}")
    print(f"in stream_show. username={username}, position={position}")
    print(f"user_display_status --> {user_display_status}")
    if username in user_display_status:
        if frame is None and user_display_status[username] is False:  # still on default.
            return

    # updating display status for each user:
    user_display_status[username] = False  # default
    if frame is not None:
        user_display_status[username] = True
    try:
        if root_call.winfo_exists():  # Check if root window still exists
            if frame is not None:
                # Display the video frame
                frame = cv2.flip(frame, 1)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame)
                img = ImageTk.PhotoImage(image=img)

                # Display the frame on the root window if it's still valid
                label = tk.Label(root_call, image=img)
                label.image = img  # Keep a reference to prevent garbage collection
                label.place(x=position[0], y=position[1], width=FRAME_SIZE[0], height=FRAME_SIZE[1])
            elif username is not None:
                # Display the username if frame is None
                frame_widget = customtkinter.CTkFrame(master=root_call, bg_color="transparent", width=FRAME_SIZE[0],
                                                      height=FRAME_SIZE[1])
                frame_widget.place(x=position[0], y=position[1])  # Ensure frame is placed at the specified position

                # Create a label frame to center the username label
                label_frame = tk.Frame(frame_widget, background=global_use_for_client.BACKGROUND_COLOR_DARK, width=FRAME_SIZE[0],
                                       height=FRAME_SIZE[1])
                label_frame.grid(row=0, column=0, padx=1, pady=1)  # Adjust padding as needed

                # Display the username label at the center of the label frame
                label_username = customtkinter.CTkLabel(master=label_frame, bg_color="transparent", text=username,
                                                        font=(global_use_for_client.FONT_STYLE, global_use_for_client.FONT_SIZE))
                label_username.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    except tk.TclError:
        print("[CALL_HANDLER]: Root window is destroyed.")
    print(f"STREAM DISPLAY - END")


def end_call():
    """
    This function ends the call by closing sockets and destroying the root window.
    :return: Nothing.
    """
    global root_call
    global_use_for_client.server_socket.close()
    global_use_for_client.server_socket_backup.close()
    for status, _ in global_use_for_client.RUN_CALL.items():
        global_use_for_client.RUN_CALL[status] = False
    root_call.destroy()


def count_active_streams():
    """
    This function is counting all that things that I need to send the server.
    :return: int
    """
    num = 0
    for status in global_use_for_client.RUN_CALL.values():
        if status:
            num += 1
    num += len(global_use_for_client.EVENTS_TO_CHECK)  # inorder to check if I have events on other's share screen.
    return num


def connect_to_server():
    """
    This function connects to the server using the specified IP and port.
    :return: None
    """
    global_use_for_client.PORT_TO_CONNECT = 56561

    print(f"{global_use_for_client.FILE_NAME}: trying to connect to the server...")

    global_use_for_client.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    global_use_for_client.server_socket.connect((global_use_for_client.IP_TO_CONNECT, global_use_for_client.PORT_TO_CONNECT))

    global_use_for_client.server_socket_backup = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    global_use_for_client.server_socket_backup.connect((global_use_for_client.IP_TO_CONNECT, global_use_for_client.PORT_TO_CONNECT))  # connecting another backup socket

    print(f"{global_use_for_client.FILE_NAME}: connection has been made with the server!")


def swap_last_on_off(path):
    """
    This function is getting a string. and replacing the last on/off with his opposite. for example: "dfkonon" --> "dfkonoff"
    :param path: string
    :return: updated string.
    """
    # Find the last occurrence of "on" and "off"
    last_on_index = path.rfind("on")
    last_off_index = path.rfind("off")

    # If "on" occurs after the last "off", replace it with "off"
    if last_on_index > last_off_index:
        return path[:last_on_index] + "off" + path[last_on_index + 2:]
    # If "off" occurs after the last "on", replace it with "on"
    elif last_off_index > last_on_index:
        return path[:last_off_index] + "on" + path[last_off_index + 3:]
    else:
        # If neither "on" nor "off" is found, return the original string
        return path


def handle_change(button, stream_type):
    """
    This function handles the change of stream type (video, voice, share screen) when the button is clicked.
    :param button: Button object
    :param stream_type: string
    :return: Nothing.
    """
    global button_external_control

    prev_path = button._image._light_image.filename
    new_path = swap_last_on_off(prev_path)
    print(f"new_path --> {new_path}")
    if global_use_for_client.RUN_CALL[stream_type]:  # True --> False (turning off)
        global_use_for_client.RUN_CALL[stream_type] = False
        global_use_for_client.CLEAR.append(f"clear {stream_type}")
        print(f"CLEAR --> {global_use_for_client.CLEAR}")
        if (stream_type == "video" and global_use_for_client.CAP is not None
                and global_use_for_client.CAMERA_NUMBER is not None):  # in order to kill camera.
            global_use_for_client.CAP.release()
            global_use_for_client.CAP = None
        elif stream_type == "voice" and global_use_for_client.AUDIO is not None and global_use_for_client.STREAM is not None:
            global_use_for_client.AUDIO, global_use_for_client.STREAM = None, None
        elif stream_type == "share screen":
            if "on" in button_external_control._image._light_image.filename:
                print(f"[CALL_HANDLER]: external control is on, needs to be off")
                time.sleep(0.1)  # to separate between the share screen removal and the external control removal
                handle_change(button_external_control, "external control")

            button_external_control.place_forget()
    else:  # False --> True (turning on)
        flag = True
        if stream_type == "video" and global_use_for_client.CAP is None:
            global_use_for_client.CAP = init_video(global_use_for_client.CAMERA_NUMBER)
            if global_use_for_client.CAP is None:
                flag = False  # don't start video, cause camera number is probably None.
                new_path = prev_path  # don't change the image too.
        elif stream_type == "voice" and global_use_for_client.AUDIO is None and global_use_for_client.STREAM is None:
            global_use_for_client.AUDIO, global_use_for_client.STREAM = init_voice_self()
        elif stream_type == "share screen":
            button_external_control.place(x=global_use_for_client.WINDOW_WIDTH / 2 - 280, y=global_use_for_client.WINDOW_HEIGHT - 200)

        print(f"changing from False to --> {flag}")
        global_use_for_client.RUN_CALL[stream_type] = flag
    image = customtkinter.CTkImage(light_image=Image.open(new_path), size=(60, 60))
    button.configure(image=image)


def send_streams():
    """
    This function constantly checks if one of the streams is on and if it is on, it's sending the stream to the server.
    REMEMBER: the sending streams socket is server_socket (NOT server_socket_backup)
    :return: Nothing.
    """
    while True:
        if count_active_streams() > 0:
            global_use_for_client.testing_functions("test_sender.txt", f"[CALL_HANDLER]: [SENDER]: I HAVE SOMETHING TO SEND. time: {datetime.datetime.now()}")
            for key, status in global_use_for_client.RUN_CALL.items():
                if status:
                    authorization = global_use_for_client.recv_data(global_use_for_client.server_socket, 3, 1, "test_sender.txt")
                    global_use_for_client.testing_functions("test_sender.txt", f"[CALL_HANDLER]: [SENDER]: AUTHORIZATION= {authorization}. time: {datetime.datetime.now()}")

                    global_use_for_client.server_socket.send(str(key).encode())
                    global_use_for_client.testing_functions("test_sender.txt", f"[CALL_HANDLER]: [SENDER]: key sent is: {key}. time: {datetime.datetime.now()}")

                    # sending the actual stream:
                    if key == "video":
                        authorization = global_use_for_client.recv_data(global_use_for_client.server_socket, 3, 1, "test_sender.txt")
                        global_use_for_client.testing_functions("test_sender.txt", f"[CALL_HANDLER]: [SENDER]: AUTHORIZATION= {authorization}. time: {datetime.datetime.now()}")

                        global_use_for_client.send_frame(global_use_for_client.server_socket, get_video())  # Send frame to server
                    elif key == "voice":
                        global_use_for_client.server_socket.sendall(get_voice(global_use_for_client.STREAM))  # send voice stream
                    elif key == "share screen":
                        authorization = global_use_for_client.recv_data(global_use_for_client.server_socket, 3, 1, "test_sender.txt")
                        global_use_for_client.testing_functions("test_sender.txt", f"[CALL_HANDLER]: [SENDER]: AUTHORIZATION= {authorization}. time: {datetime.datetime.now()}")

                        global_use_for_client.send_frame(global_use_for_client.server_socket, get_share_screen())  # Send frame to server

                    global_use_for_client.testing_functions("test_sender.txt", f"[CALL_HANDLER]: [SENDER]: {key.upper()} SENT !. time: {datetime.datetime.now()}")

                for username in global_use_for_client.EVENTS_TO_CHECK:  # running on all usernames I can remotely control.
                    global_use_for_client.testing_functions("test_sender.txt", f"[CALL_HANDLER]: [SENDER]: {username} allows control. time: {datetime.datetime.now()}")
                    if username in global_use_for_client.ALL_EVENTS.copy().keys():  # if one of the windows with events is username
                        global_use_for_client.testing_functions("test_sender.txt", f"[CALL_HANDLER]: [SENDER]: {username} in dictionary. time: {datetime.datetime.now()}")

                        for event in global_use_for_client.ALL_EVENTS.copy()[username]:
                            # event example: {'type': 'mouse', 'x': 1159, 'y': 687, 'button': 'left', 'pressed': True}
                            authorization = global_use_for_client.recv_data(global_use_for_client.server_socket, 3, 1, "test_sender.txt")
                            global_use_for_client.testing_functions("test_sender.txt", f"[CALL_HANDLER]: [SENDER]: AUTHORIZATION= {authorization}. time: {datetime.datetime.now()}")

                            message = f"{username}::{event}"
                            global_use_for_client.testing_functions("test_sender.txt", f"[CALL_HANDLER]: [SENDER]: message I'm about to send --> {message}. time: {datetime.datetime.now()}")

                            global_use_for_client.server_socket.send(message.encode())  # sending --> username and the event to run on him.
                            global_use_for_client.ALL_EVENTS[username].remove(event)
                            global_use_for_client.testing_functions("test_sender.txt", f"[CALL_HANDLER]: [SENDER]: message sent and event removed successfully from dictionary. time: {datetime.datetime.now()}")

                if global_use_for_client.CLEAR:  # not empty.
                    global_use_for_client.testing_functions("test_sender.txt", f"[CALL_HANDLER]: [SENDER]: letting the server know he should reset these values: {global_use_for_client.CLEAR}. time: {datetime.datetime.now()}")
                    for stream_type in global_use_for_client.CLEAR:
                        authorization = global_use_for_client.recv_data(global_use_for_client.server_socket, 3, 1, "test_sender.txt")
                        global_use_for_client.testing_functions("test_sender.txt", f"[CALL_HANDLER]: [SENDER]: AUTHORIZATION= {authorization}. time: {datetime.datetime.now()}")

                        global_use_for_client.server_socket.send(stream_type.encode())
                        global_use_for_client.testing_functions("test_sender.txt", f"[CALL_HANDLER]: [SENDER]: stream_type: {stream_type} sent successfully! time: {datetime.datetime.now()}")

                global_use_for_client.CLEAR = []
            # time.sleep(0.01)
            global_use_for_client.testing_functions("test_sender.txt", f"[CALL_HANDLER]: [SENDER]: ITERATION END. time: {datetime.datetime.now()}")
        else:
            global_use_for_client.testing_functions("test_sender.txt", f"[CALL_HANDLER]: [SENDER]: 0 running streams on my side. time: {datetime.datetime.now()}")
            time.sleep(0.5)


def get_position(username):
    global user_positions
    if username not in user_positions:
        user_positions[username] = calculate_position()  # Assign a position to the user
    return user_positions[username]


def calculate_position():
    global user_positions
    x_offset = 100
    y_offset = 200
    space_between = 200  # space between each cube
    max_columns = 3  # maximum number of streams per row
    num_users = len(user_positions)

    x = x_offset + (num_users % max_columns) * (FRAME_SIZE[0] + space_between)
    y = y_offset + (num_users // max_columns) * (FRAME_SIZE[1] + space_between)

    return (x, y)


def receive_streams():
    """
    This function constantly checks if one of the streams is on and if it is on, it's sending the stream to the server.
    the purpose of temp, types, prev_username is to decide whether I should create a widget on the window for that stream type.
    for example: I have video and voice from the same user, I wouldn't want to create 2 widgets for that purpose, I would create only one.
                but if the user only had voice, then I would want to create a widget... in order to that I need to let
                client know the name of the username so I would know to do the separation.
    REMEMBER: the receiving streams socket is server_socket_backup (NOT server_socket)
    :return: Nothing.
    """
    global user_display_status

    frame = None
    username = global_use_for_client.my_username
    green_light = True
    while True:
        if global_use_for_client.call_mode:
            try:
                global_use_for_client.testing_functions("test_receive.txt", f"[CALL_HANDLER]: [RECEIVER]: start")
                if green_light:
                    stream_show(username, frame, get_position(username))

                global_use_for_client.testing_functions("test_receive.txt", f"[CALL_HANDLER]: [RECEIVER]: About To Send GO4. time: {datetime.datetime.now()}")
                global_use_for_client.server_socket_backup.send("GO4".encode())

                global_use_for_client.testing_functions("test_receive.txt", f"[CALL_HANDLER]: [RECEIVER]: Waiting to receive username, stream_type. time: {datetime.datetime.now()}")
                data = global_use_for_client.recv_data(global_use_for_client.server_socket_backup, 128, 1, "test_receive.txt")

                global_use_for_client.testing_functions("test_receive.txt", f"[CALL_HANDLER]: [RECEIVER]: data: {data}. time: {datetime.datetime.now()}")
                username, stream_type = data.split(":")
                global_use_for_client.testing_functions("test_receive.txt", f"[CALL_HANDLER]: [RECEIVER]: username: {username}. stream_type: {stream_type}. time: {datetime.datetime.now()}")

                green_light = filter_real_username(username)  # checks if the username is suspicious.

                time.sleep(0.01)
                if green_light:  # if the username seams okay.
                    if stream_type == "video":
                        global_use_for_client.server_socket_backup.send("GO5".encode())
                        frame = global_use_for_client.receive_frame(global_use_for_client.server_socket_backup)
                        if frame is None:
                            global_use_for_client.testing_functions("test_receive.txt", "[CALL_HANDLER]: [RECEIVER]: Error: *2* Failed to receive message.")
                            break
                        global_use_for_client.testing_functions("test_receive.txt", f"[CALL_HANDLER]: [RECEIVER]: video updated !".upper())

                    elif stream_type == "share screen":
                        global_use_for_client.server_socket_backup.send("GO6".encode())
                        stream = global_use_for_client.receive_frame(global_use_for_client.server_socket_backup)
                        if stream is None:
                            global_use_for_client.testing_functions("test_receive.txt", "[CALL_HANDLER]: [RECEIVER]: share screen Falied")
                            break
                        global_use_for_client.testing_functions("test_receive.txt", f"[CALL_HANDLER]: [RECEIVER]: share screen received --> {stream}. time: {datetime.datetime.now()}")

                        if username != global_use_for_client.my_username:
                            # the line below controls the resizing of the share screen.
                            stream = cv2.resize(stream, (global_use_for_client.WINDOW_WIDTH - 20, global_use_for_client.WINDOW_HEIGHT - 80))
                            cv2.imshow(username, stream)  # VERY IMPORTANT TO NAME THIS WINDOW WITH THE username I GOT !
                            cv2.moveWindow(username, 0, 0)

                    elif stream_type == "voice":
                        stream = global_use_for_client.recv_data(global_use_for_client.server_socket_backup, global_use_for_client.CHUNK, 1, "test_receive.txt")
                        global_use_for_client.STREAM_OUT.write(stream)
                    elif stream_type == "external control":
                        if username not in global_use_for_client.EVENTS_TO_CHECK and username != global_use_for_client.my_username:
                            global_use_for_client.testing_functions("test_receive.txt", f"[CALL_HANDLER]: [RECEIVER]: appending {username} to events_to_check list.")
                            global_use_for_client.EVENTS_TO_CHECK.append(username)
                    elif stream_type == "events":
                        global_use_for_client.testing_functions("test_receive.txt", f"[CALL_HANDLER]: [RECEIVER]: receiving an event. time: {datetime.datetime.now()}")
                        event_to_execute = global_use_for_client.recv_data(global_use_for_client.server_socket_backup, 128, 1, "test_receive.txt")
                        event_to_execute = str(event_to_execute)
                        try:
                            event_to_execute = eval(event_to_execute)
                            global_use_for_client.testing_functions("test_receive.txt", f"[CALL_HANDLER]: [RECEIVER]: event_to_execute --> {event_to_execute}")
                            global_use_for_client.execute_event(event_to_execute)
                            global_use_for_client.testing_functions("test_receive.txt", f"[CALL_HANDLER]: [RECEIVER]: executed event successfully!")
                        except Exception as e:
                            global_use_for_client.testing_functions("test_receive.txt", f"[CALL_HANDLER]: [RECEIVER]: error trying to execute event. {e}")
                    elif stream_type == "default":
                        frame = None

                    global_use_for_client.testing_functions("test_receive.txt", "[CALL_HANDLER]: [RECEIVER]: ------------------------------------------------------------------STREAM RECEIVED------------------------------------------------------------------")

                    if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit if 'q' is pressed
                        break
                else:
                    global_use_for_client.testing_functions("test_receive.txt", f"[CALL_HANDLER]: [RECEIVER]: I got a weird username.")

            except Exception as e:
                global_use_for_client.testing_functions("test_receive.txt", f"[CALL_HANDLER]: [RECEIVER]: Error: {e}")
        else:
            global_use_for_client.testing_functions("test_receive.txt", f"[CALL_HANDLER]: [RECEIVER]: call mode is off.")
            time.sleep(0.5)


def call_structure():
    """
    This function manages the overall call structure, including initializing video/voice streams and handling user interactions.
    :return: Nothing.
    """
    global root_call, button_video, button_share_screen, button_voice, button_external_control

    root_call = tk.Tk()
    root_call.title(f"Call Handler- {global_use_for_client.my_username}")

    root_call.tk_setPalette(background=global_use_for_client.INCOMING_CALL_COLOR, foreground="black", activeForeground="black",
                            activeBackground=global_use_for_client.INCOMING_CALL_COLOR)
    root_call.geometry(f"{global_use_for_client.WINDOW_WIDTH}x{global_use_for_client.WINDOW_HEIGHT - 45}")

    image_external_control = customtkinter.CTkImage(light_image=Image.open(fr"{os.getcwd()}\Pictures\external_control_off.png"), size=(60, 60))
    image_video = customtkinter.CTkImage(light_image=Image.open(fr"{os.getcwd()}\Pictures\video_off.png"), size=(60, 60))
    image_share_screen = customtkinter.CTkImage(light_image=Image.open(fr"{os.getcwd()}\Pictures\share_screen_off.png"), size=(60, 60))
    image_voice = customtkinter.CTkImage(light_image=Image.open(fr"{os.getcwd()}\Pictures\voice_off.png"), size=(60, 60))
    image_end_call = customtkinter.CTkImage(light_image=Image.open(fr"{os.getcwd()}\Pictures\end_call.png"), size=(60, 60))

    # Define buttons
    button_external_control = customtkinter.CTkButton(master=root_call, text="", width=50, image=image_external_control, fg_color="transparent", hover_color=global_use_for_client.HOVER_COLOR)  # incharge of allowing others to remotely control this pc.
    button_video = customtkinter.CTkButton(master=root_call, text="", width=50, image=image_video, fg_color="transparent", hover_color=global_use_for_client.HOVER_COLOR)
    button_share_screen = customtkinter.CTkButton(master=root_call, text="", width=50, image=image_share_screen, fg_color="transparent", hover_color=global_use_for_client.HOVER_COLOR)
    button_voice = customtkinter.CTkButton(master=root_call, text="", width=50, image=image_voice, fg_color="transparent", hover_color=global_use_for_client.HOVER_COLOR)
    end_call_button = customtkinter.CTkButton(master=root_call, text="", width=50, image=image_end_call, command=end_call, fg_color="transparent", hover_color=global_use_for_client.HOVER_COLOR)

    # Set commands using functools.partial
    button_external_control.configure(command=partial(handle_change, button_external_control, "external control"))
    button_video.configure(command=partial(handle_change, button_video, "video"))
    button_share_screen.configure(command=partial(handle_change, button_share_screen, "share screen"))
    button_voice.configure(command=partial(handle_change, button_voice, "voice"))

    button_video.place(x=global_use_for_client.WINDOW_WIDTH / 2 - 200, y=global_use_for_client.WINDOW_HEIGHT - 200)
    button_share_screen.place(x=global_use_for_client.WINDOW_WIDTH / 2 - 120, y=global_use_for_client.WINDOW_HEIGHT - 200)
    button_voice.place(x=global_use_for_client.WINDOW_WIDTH / 2 - 40, y=global_use_for_client.WINDOW_HEIGHT - 200)
    end_call_button.place(x=global_use_for_client.WINDOW_WIDTH / 2 + 40, y=global_use_for_client.WINDOW_HEIGHT - 200)

    root_call.mainloop()


def main(call_type=""):
    """
    This function serves as the entry point for the application, connecting sockets to the server
    ,setting up necessary configurations and starting the call GUI.
    :return: Nothing.
    """
    global root_call, button_video, button_share_screen, button_voice

    connect_to_server()  # connecting to server.
    threading.Thread(target=call_structure, ).start()
    global_use_for_client.AUDIO_OUT, global_use_for_client.STREAM_OUT = init_voice_out()

    global_use_for_client.clear_file("test_sender.txt")
    global_use_for_client.clear_file("test_receive.txt")

    if "video" in call_type:
        if global_use_for_client.CAP is None and global_use_for_client.CAMERA_NUMBER is not None:
            global_use_for_client.CAP = init_video(global_use_for_client.CAMERA_NUMBER)
        handle_change(button_video, "video")

    elif "voice" in call_type:
        global_use_for_client.AUDIO, global_use_for_client.STREAM = init_voice_self()
        handle_change(button_voice, "voice")

    send = threading.Thread(target=send_streams, daemon=True)
    send.start()

    receive = threading.Thread(target=receive_streams, daemon=True)
    receive.start()

    capture_events = threading.Thread(target=global_use_for_client.capture_events, )
    capture_events.start()

    # resetting events every 7 seconds (the waiting time is dynamic, I can change him as needed)
    reset_events_for_given_time = threading.Thread(target=global_use_for_client.reset_events, args=(7,))
    reset_events_for_given_time.start()

    time.sleep(0.1)


if __name__ == "__main__":
    main()