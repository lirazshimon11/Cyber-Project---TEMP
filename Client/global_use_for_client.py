import os
import socket
import time
import pygetwindow
from pynput import mouse, keyboard
from PIL import ImageGrab
import base64
import pyautogui
import pickle
import struct
import cv2
from pygrabber.dshow_graph import FilterGraph

# COLORS:
TEXT_COLOR = "#9498A0"
BACKGROUND_COLOR = "#2B2D31"  # "#2B2D31"
BACKGROUND_COLOR_DARK = "#191A1C"
HOVER_COLOR = "#36373D"
TEXT_COLOR_BRIGHT = "#FFFFF9"
ADD_FRIEND_HOVER_COLOR = "#248046"
LINE_COLOR = "#313338"
SEND_REQUEST_COLOR = "#5865F2"
INCOMING_CALL_COLOR = "#111214"
IMPORTANT_REQUEST_COLOR = "#B5BAB6"
ERROR_COLOR = "#CC0000"
COLOR = "#5865F2"

# FONT AND SIZE:
FONT_STYLE = "Aharoni"
FONT_SIZE = 28
FONT_SIZE_SMALL = 18
INCORRECT_INFO = "Incorrect username or password.."
INCORRECT_INFO2 = "Hm, didn't work. Double check that the username is correct."
INVALID_INFO = "Invalid information.."

ROOT = None
SCREEN_WIDTH, SCREEN_HEIGHT = ImageGrab.grab().size  # screen's width and height.
WINDOW_WIDTH, WINDOW_HEIGHT = SCREEN_WIDTH - 364, SCREEN_HEIGHT - 216
my_username = "a"  # default
IP_TO_CONNECT = "localhost"
PORT_TO_CONNECT = 49101  # 49101 / 56561 ARE PORT FORWARDING INSIDE MY PERSONAL ROUTER
FILE_NAME = "HOME"  # default..
server_socket = None
server_socket_backup = None
MAIN_KEY = b''
is_on_chat_screen = False
add_friends_button = None  # Initialize with the appropriate value
send_msg_entry = None
select_friends_button = None
time_label = None
MENU_LAYOUTS = []  # HOME will use this variable inorder to avoid killing menu layouts
call_mode = False  # call is activated.
# "external control" --> allow/not remote control over this pc. "events access" --> allow searching on my events.
RUN_CALL = {"video": False, "voice": False, "share screen": False, "external control": False}
EVENTS_TO_CHECK = []  # usernames that I need to check if I have events on their share screen.
CLEAR = []  # for example: ["clear video", "clear share screen"]. for each value from this list-the server should reset.
CAP = None
AUDIO, STREAM = None, None
AUDIO_OUT, STREAM_OUT = None, None
X_ALIGNMENT = 0
Y_ALIGNMENT = 0
MAX_CHARACTERS_AMOUNT = 50
ALL_EVENTS = {}
SEPARATOR = b":::::::::"  # to separate between the cipher, tag, and nonce
CHUNK = 1024


def reset_root(root=None):
    """
    Each and every time I'm going to different display, I'm going through this function.
    This function is meant to reset all dynamic layouts from the root, and reset variables.
    :param root: tkinter
    :return:
    """
    global is_on_chat_screen
    print(f"{FILE_NAME}: about to reset root!")
    is_on_chat_screen = False
    if root:
        # Remove all widgets from the root
        for widget in root.winfo_children():
            if widget not in MENU_LAYOUTS:
                widget.destroy()
    print(f"{FILE_NAME}: root is clean")


def decrypt_with_base64(encrypted_string):
    encrypted_bytes = encrypted_string.encode('utf-8')
    decrypted_bytes = base64.b64decode(encrypted_bytes)
    decrypted_string = decrypted_bytes.decode('utf-8')
    return decrypted_string


def get_available_cameras():

    devices = FilterGraph().get_input_devices()
    available_cameras = {}

    for device_index, device_name in enumerate(devices):
        available_cameras[device_index] = device_name

    return available_cameras


def check_camera_availability(preference: str = None):
    """
    This function is getting all the cameras, and checks who's available for use, then returns an index of a camera
    example of the available cameras after the check: {0: "Camera HD User Facing", 1: "Camera PC-LM1E Camera"} or {}...
    :param preference: string. None --> default (the first I find) / name of a camera.
    :return: int / None (if there isn't one available camera). camera index.
    """
    all_cameras = get_available_cameras()  # get all cameras.
    available_cameras = all_cameras.copy()
    for index, name in all_cameras.items():
        camera = cv2.VideoCapture(index)
        if camera.isOpened():
            for _ in range(5):  # Try capturing frames in a loop
                _, frame = camera.read()
                if frame is None:
                    available_cameras.pop(index)  # the camera is already occupied.
                    break  # Exit loop if frame is captured successfully
    # print(f"available cameras --> {available_cameras}")
    if available_cameras:  # there are available cameras... I'm picking the first one.
        if preference is not None:  # preference given. checking if exists.
            print(f"preference in check")
            for index, camera_name in available_cameras.items():
                if camera_name == preference:
                    return index
        else:  # return default.
            return list(available_cameras.keys())[0]  # return the first available camera from the dictionary.
    return None  # No available cameras


CAMERA_NUMBER = check_camera_availability()  # currently the default.
print(f"camera number is {CAMERA_NUMBER}")


def recv_data(conn, bytes_num: int, wait: float, file_path="example.txt", decode=True):
    conn.settimeout(wait)
    while True:
        try:
            testing_functions(file_path, f"[CALL_HANDLER]: Waiting For Answer..")
            data = conn.recv(bytes_num)
            if data:
                conn.settimeout(None)
                if decode:
                    data = data.decode()
                testing_functions(file_path, f"[CALL_HANDLER]: Received Successfully!")

                return data
        except socket.timeout:
            testing_functions(file_path, f"[CALL_HANDLER]: SOCKET TIMEOUT")
            continue


def send_frame(conn, frame):
    try:
        message_data = pickle.dumps(frame)
        message_size = struct.pack("!I", len(message_data))

        conn.sendall(message_size)
        conn.sendall(message_data)
    except Exception as e:
        print(f"[GLOBAL_USE_FOR_CLIENT]: failed to send frame - {e}")


def receive_frame(conn):
    try:
        message_size_data = recv_data(conn, 4, 0.001, "test_receive.txt", False)
        if not message_size_data:
            return None
        message_size = struct.unpack(">L", message_size_data)[0]
        message_data = b""
        while len(message_data) < message_size:
            packet = recv_data(conn, message_size - len(message_data), 0.001, "test_receive.txt", False)
            if not packet:
                return None
            message_data += packet
        frame = pickle.loads(message_data)
        return frame
    except:
        print(f"[GLOBAL_USE_FOR_CLIENT]: failed to receive frame")
        return None


def capture_events():
    """
    Captures mouse and keyboard events using pyautogui
    Inserts each event into the ALL_EVENTS dictionary
    """

    def on_mouse_event(x, y, button, pressed):
        # Map Button enum to lowercase string
        button = str(button)
        if '.left' in button or '.right' in button or '.middle' in button:
            button_str = button.split('.')[1]
            current_event = {"type": "mouse", "x": x, "y": y, "button": button_str, "pressed": pressed}
            try:
                current_window = pygetwindow.getActiveWindow().title
                if current_window not in ALL_EVENTS:
                    ALL_EVENTS[current_window] = []
                ALL_EVENTS[current_window].append(current_event)
            except Exception as e:
                print(f"[GLOBAL_USE_FOR_CLIENT]: error in on_mouse_event --> {e}")

    def on_keyboard_event(key, pressed):
        try:
            key_char = key.char
        except AttributeError:
            key = str(key)
            if '_l' in key:  # sort for 'left'. for instance: 'alt_l', 'ctrl_l'
                if 'caps' not in key:
                    key = key.replace('_l', 'left')
                else:  # capslock
                    key = key.replace('_l', 'lock')

            elif '_r' in key:
                key = key.replace('_r', 'right')
            if 'Key.' in key:
                key = key.replace('Key.', '')
            key_char = key

        current_event = {"type": "keyboard", "key": key_char, "pressed": pressed}
        if key_char is not None:
            try:
                current_window = pygetwindow.getActiveWindow().title
                if current_window not in ALL_EVENTS:
                    ALL_EVENTS[current_window] = []
                ALL_EVENTS[current_window].append(current_event)
            except Exception as e:
                print(f"[GLOBAL_USE_FOR_CLIENT]: error in on_keyboard_event --> {e}")
    # Set up listeners for mouse and keyboard events
    mouse_listener = mouse.Listener(on_click=on_mouse_event)
    keyboard_listener = keyboard.Listener(on_press=lambda k: on_keyboard_event(k, True),
                                          on_release=lambda k: on_keyboard_event(k, False))

    try:
        # Start capturing events
        print("Start capturing events")
        mouse_listener.start()
        keyboard_listener.start()
        print("Start capturing events")
        mouse_listener.join()
        keyboard_listener.join()
    except KeyboardInterrupt:
        # Clean up listeners if interrupted
        mouse_listener.stop()
        keyboard_listener.stop()
        print("Event capturing stopped.")


def reset_events(wait: int):
    """
    Resets the ALL_EVENTS the dictionary's values to an empty [] every {wait} seconds.
    """
    while True:
        time.sleep(wait)
        print(f"ALL_EVENTS #BEFORE RESET# --> {ALL_EVENTS}")
        for key in ALL_EVENTS:
            ALL_EVENTS[key] = []
        print(f"ALL_EVENTS #AFTER RESET# --> {ALL_EVENTS}")


#
# capture_events = threading.Thread(target=capture_events, )
# capture_events.start()
#
# # resetting events every 2 seconds (the waiting time is dynamic, I can change him as needed)
# reset_events_for_given_time = threading.Thread(target=reset_events, args=(3,))
# reset_events_for_given_time.start()
#
# time.sleep(0.1)


def execute_event(event):
    """
    This function's purpose is to get an event, and execute this event (if possible)
    """
    print("In execute_event.")
    if event['type'] == 'mouse':
        if event['pressed']:
            if event['button'] == 'right' or event['button'] == 'left' or event['button'] == 'middle':
                pyautogui.mouseDown(event['x'], event['y'], button=event['button'])
        else:
            if event['button'] == 'right' or event['button'] == 'left' or event['button'] == 'middle':
                pyautogui.mouseUp(button=event['button'])
    elif event['type'] == 'keyboard':
        if event['key'] == 'cmd':
            event['key'] = 'win' if event['key'] not in pyautogui.KEY_NAMES else event['key']

        if event['key'] in pyautogui.KEY_NAMES:  # if the key can be executed via pyautogui range of options.
            if event['pressed']:
                pyautogui.keyDown(event['key'])
            else:
                pyautogui.keyUp(event['key'])
        else:
            print(f"The Given Key Doesn't Exist In The KEY_NAMES List.")


def center_data(data, total_space):
    # Calculate the number of spaces needed on each side
    spaces_needed = total_space - len(data)
    left_spaces = spaces_needed // 2
    right_spaces = spaces_needed - left_spaces

    # Construct the centered string
    centered_data = " " * left_spaces + data + " " * right_spaces

    return centered_data


def testing_functions(file_path, print):
    """
    This function is saving printings inside a file.
    :param file_path: string
    :param print: string
    :return: Nothing.
    """
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            pass

    with open(file_path, 'a') as file:
        file.write(print + '\n')


def clear_file(path):
    if os.path.exists(path):
        with open(path, 'w') as file:
            file.truncate(0)
            print("File cleared successfully.")
    else:
        print("File does not exist.")



