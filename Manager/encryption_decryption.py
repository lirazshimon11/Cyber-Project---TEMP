import pickle
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import global_use_for_server


def generate_AES_key():
    """
    This function's purpose is to generate a new AES key.
    :return: AES key in bytes
    """
    # the key is bytes so we can send it using sockets
    # 32 bytes is size of key
    key = get_random_bytes(32)
    return key


def generate_RSA_key():
    """
    this function generates my private rsa key.
    :return:
    """
    # 2048 bit is size of key
    key = RSA.generate(2048)
    return key


def bytes_to_key(bytes):
    """
    This function's purpose is to convert bytes to an RSA key object.
    :param bytes: RSA key in bytes
    :return: RSA key object
    """
    return RSA.import_key(bytes)


def key_to_bytes(key):
    """
    This function's purpose is to convert an RSA key object to bytes.
    :param key: RSA key object
    :return: RSA key in bytes
    """
    return key.export_key()


def RSA_encryption(data, key_bytes):
    """
    This function's purpose is to encrypt data using RSA encryption.
    :param data: Data to be encrypted
    :param key_bytes: RSA key in bytes
    :return: Encrypted data in bytes
    """
    key = bytes_to_key(key_bytes)
    cipher = PKCS1_OAEP.new(key)
    return cipher.encrypt(data)


def RSA_decryption(data, key):
    """
    This function's purpose is to decrypt data using RSA encryption.
    :param data: Data to be decrypted
    :param key: RSA key object
    :return: Decrypted data in bytes
    """
    cipher = PKCS1_OAEP.new(key)
    return cipher.decrypt(data)


def AES_encryption(data, key):
    """
    This function's purpose is to encrypt data using AES encryption.
    :param data: Data to be encrypted
    :param key: AES key in bytes
    :return: Tuple containing ciphertext, tag, and nonce
    """
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return ciphertext, tag, cipher.nonce


def AES_encryption_for_server(data, key):
    """
    This function's purpose is to encrypt data using AES encryption for server.
    :param data: Data to be encrypted
    :param key: AES key in bytes
    :return: Tuple containing ciphertext and nonce
    """
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext = cipher.encrypt(data)
    return ciphertext, cipher.nonce


def AES_decryption(data, key, nonce):
    """
    This function's purpose is to decrypt data using AES encryption.
    :param data: Data to be decrypted
    :param key: AES key in bytes
    :param nonce: Nonce used during encryption
    :return: Decrypted data in bytes
    """
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(data)
    return plaintext


def AES_decryption_for_server(data, key, nonce, tag):
    """
    This function's purpose is to decrypt and verify data using AES encryption.
    :param data: Data to be decrypted
    :param key: AES key in bytes
    :param nonce: Nonce used during encryption
    :param tag: Tag used during encryption
    :return: Decrypted data in bytes
    """
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt_and_verify(data, tag)
    return plaintext


def decrypting_messages(cipher_and_nonce, AES_key):
    """
    This function's purpose is to decrypt messages using AES encryption.
    :param cipher_and_nonce: Tuple containing ciphertext and nonce
    :param AES_key: AES key in bytes
    :return: Decrypted data in bytes
    """
    cipher, nonce = cipher_and_nonce[0], cipher_and_nonce[1]
    decrypted_data = AES_decryption(cipher, AES_key, nonce)
    return decrypted_data


def decrypting_requests_for_server(cipher_and_nonce, main_key):
    """
    This function's purpose is to decrypt requests for the server using AES encryption.
    :param cipher_and_nonce: Ciphertext and nonce separated by a separator
    :param main_key: AES key in bytes
    :return: Decrypted data in bytes
    """
    cipher, tag, nonce = cipher_and_nonce.split(global_use_for_server.SEPARATOR)
    decrypted_data = AES_decryption_for_server(cipher, main_key, nonce, tag)
    return decrypted_data


# def decrypting_messages_for_video(cipher_and_nonce, AES_key):
#     parts = cipher_and_nonce.split(global_use_for_server.SEPARATOR)
#     cipher = parts[0]
#     # tag = parts[1]
#     nonce = parts[2]
#
#     decrypted_data = AES_decryption(cipher, AES_key, nonce)
#     return decrypted_data


def handle_keys_exchange_for_server(client_socket):
    """
    This function's purpose is to handle the key exchange with the client.
    :param client_socket: Client socket object
    :return: Decrypted main key in bytes
    """
    ############################# START - Exchange keys #############################
    private_key = generate_RSA_key()  # private rsa key.
    public_key = key_to_bytes(private_key.public_key())  # public RSA key (in bytes)
    client_socket.send(public_key)  # No need to encode because it's already in bytes

    aes_encrypted_key = client_socket.recv(2048)  # receiving --> encrypted key
    MAIN_KEY = RSA_decryption(aes_encrypted_key, private_key)
    print(f"                [ENCRYPTION_DECRYPTION]: main Key={MAIN_KEY}")

    ############################# END   - Exchange keys #############################

    # CLIENTS[client_socket] = MAIN_KEY  # inserting new key and value inside the dictionary.
    # # CLIENTS STRUCTURE: {(socket1, socket1_backup): key1, socket2, socket2_backup): key2, etc...}
    # return CLIENTS  # not returning the MAIN_KEY because he is already inside the dictionary.

    return MAIN_KEY


def handle_keys_exchange_for_client(server_socket):
    """
    This function's purpose is to handle the key exchange with the server.
    :param server_socket: Server socket object
    :return: Decrypted main key in bytes
    """
    global MAIN_KEY
    ############################# START - Exchange keys #############################
    server_public_key = server_socket.recv(1024).decode()  # receiving --> client's public rsa key
    AES_key = generate_AES_key()
    server_public_key_encrypted = RSA_encryption(AES_key, server_public_key)  # encrypting with rsa
    server_socket.send(server_public_key_encrypted)  # sending --> encrypted AES key
    print(f"                [ENCRYPTION_DECRYPTION]: main key={AES_key}")
    ############################# END   - Exchange keys #############################
    MAIN_KEY = AES_key
    return MAIN_KEY


################################################# AFTER KEYS EXCHANGE #################################################


def encrypt_msg_for_server(data, main_key):
    """
    This function's purpose is to encrypt a message for the server using AES encryption.
    :param data: Data to be encrypted
    :param main_key: AES key in bytes
    :return: Encrypted message with nonce appended
    """
    print(f"                [ENCRYPTION_DECRYPTION]: BEFORE: {data}")
    data = data.encode()
    cipher, nonce = AES_encryption_for_server(data, main_key)
    cipher_and_nonce = cipher + global_use_for_server.SEPARATOR + nonce  # combining then to one, in order to send them both in one time.
    print(f"                [ENCRYPTION_DECRYPTION]: AFTER {cipher_and_nonce}")
    return cipher_and_nonce


def encrypt_msg_for_client_and_dictionary(data, main_key):
    """
    This function's purpose is to encrypt a message for the client using AES encryption.
    :param data: Data to be encrypted
    :param main_key: AES key in bytes
    :return: Encrypted message with tag and nonce appended
    """
    print(f"                [ENCRYPTION_DECRYPTION]: BEFORE: {data}")

    data = pickle.dumps(data)
    cipher, tag, nonce = AES_encryption(data, main_key)
    cipher_and_nonce_and_tag = b"".join([cipher, global_use_for_server.SEPARATOR, tag, global_use_for_server.SEPARATOR, nonce])  # combining them to send in one transmission
    print(f"                [ENCRYPTION_DECRYPTION]: AFTER- {cipher_and_nonce_and_tag}")
    return cipher_and_nonce_and_tag


def receive_message(conn, key, need="string", wait=None):
    """
    This function is getting the socket and the key, then receives the regular encrypted message from the server and
    decrypts it.
    :param conn: socket
    :param key: main key for communicating safely.
    :param need: string. string/dictionary
    :param wait: int/float
    :return: decrypted message
    """
    if wait is not None and isinstance(wait, int) or isinstance(wait, float):
        conn.settimeout(wait)

    print(f"\n                [ENCRYPTION_DECRYPTION]: {conn}. in receive_message")
    try:
        conn.send("GO".encode())  # sending --> to let the other side know I'm ready for receive protocol.
        print(f"                [ENCRYPTION_DECRYPTION]: {conn}. in receive_message")
        bytes_length = conn.recv(4).decode()
        print(f"                [ENCRYPTION_DECRYPTION]: {conn}. before bytes length ==> {bytes_length}")
        bytes_length = int(bytes_length)
        print(f"                [ENCRYPTION_DECRYPTION]: {conn}. bytes length ==> {bytes_length}")
        if need == "dictionary":
            data_encrypted = conn.recv(bytes_length)
            print(f"                [ENCRYPTION_DECRYPTION]: {conn}. received #encrypted# ==> {data_encrypted}")
            data_decrypted = decrypting_requests_for_server(data_encrypted, key)
            data = pickle.loads(data_decrypted)
            print(f"                [ENCRYPTION_DECRYPTION]: {conn}. received #decrypted# ==> {data}")
        else:
            cipher_and_nonce = conn.recv(bytes_length).split(global_use_for_server.SEPARATOR)
            print(f"                [ENCRYPTION_DECRYPTION]: {conn}. received #encrypted# ==> {cipher_and_nonce}")
            data_bytes = decrypting_messages(cipher_and_nonce, key)
            data = data_bytes.decode()
            print(f"                [ENCRYPTION_DECRYPTION]: {conn}. received #decrypted# ==> {data}")
        return data
    except Exception as e:
        print(f"                [ENCRYPTION_DECRYPTION]: Error in receive_message {e}")


def protocol_send_for_server(socket_, data, main_key, type_to_encrypt="string"):
    """
    This function's purpose is to send encrypted data to the client using a specified encryption type.
    :param socket_: Socket object for server communication
    :param data: Data to be sent
    :param main_key: Main AES key in bytes
    :param type_to_encrypt: Specifies the encryption type ("string" or "dictionary")
    :return: Nothing
    """
    try:
        print(f"\n                [ENCRYPTION_DECRYPTION]: {socket_}. in protocol send for server")
        print(f"                [ENCRYPTION_DECRYPTION]: {socket_}. {socket_.recv(2).decode()}")  # receive something whenever the other side is ready.
        if type_to_encrypt == "dictionary":
            print(f"                [ENCRYPTION_DECRYPTION]: {socket_}. dictionary type")
            encrypted = encrypt_msg_for_client_and_dictionary(data, main_key)
        else:
            encrypted = encrypt_msg_for_server(data, main_key)
        print(f"                [ENCRYPTION_DECRYPTION]: {socket_}. encrypted data = {encrypted}")
        encrypted_length = str(len(encrypted))
        print(f"                [ENCRYPTION_DECRYPTION]: {socket_}. encrypted length = {encrypted_length}")
        socket_.send(encrypted_length.encode())
        socket_.send(encrypted)
        print(f"                [ENCRYPTION_DECRYPTION]: {socket_}. data sent!")
    except:
        print(f"                [ENCRYPTION_DECRYPTION]: Error in protocol send for server")


def protocol_send_for_client(socket_, data, main_key):
    """
    This function's purpose is to send encrypted data to the server.
    :param socket_: Socket object for client communication
    :param data: Data to be sent
    :param main_key: Main AES key in bytes
    :return: Nothing
    """
    try:
        print(f"\n                [ENCRYPTION_DECRYPTION]: {socket_}. in protocol send for client")
        authorized = socket_.recv(2).decode()
        if authorized == "GO":
            print(f"                [ENCRYPTION_DECRYPTION]: {socket_}. unencrypted data = {data}")
            encrypted = encrypt_msg_for_client_and_dictionary(data, main_key)
            encrypted_length = str(len(encrypted))
            print(f"                [ENCRYPTION_DECRYPTION]: {socket_}. encrypted length = {encrypted_length}")
            socket_.send(encrypted_length.encode())
            socket_.send(encrypted)
            print(f"                [ENCRYPTION_DECRYPTION]: {socket_}. data sent!")
    except:
        print(f"                [ENCRYPTION_DECRYPTION]: Error in protocol send for client")