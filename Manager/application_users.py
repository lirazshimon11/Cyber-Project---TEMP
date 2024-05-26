import json
import os
import sqlite3
import global_use_for_server

FILE_NAME = "[APPLICATION_USERS]"
DB_NAME = 'users.db'


class Users:
    """
    Class to manage user data in a SQLite database.

    Attributes:
        tablename (str): Name of the table storing user data.
        fullname (str): Column name for user's full name.
        email (str): Column name for user's email.
        username (str): Column name for user's username.
        password (str): Column name for user's password.
        phone (str): Column name for user's phone number.
        notifications (str): Column name for user's notifications.
        friends (str): Column name for user's friends.
        privatechat (str): Column name for user's private chat messages.
        important (str): Column name for user's important messages.
    """
    def __init__(self, tablename="users", fullname="fullname", email="email", username="username", password="password",
                 phone="phone", notifications="notifications", friends="friends", privatechat="privatechat",
                 important="important"):

        """
        Initializes the Users class.
        :param tablename: str. Name of the table storing user data (default is "users").
        :param fullname: str. Column name for user's full name (default is "fullname").
        :param email: str. Column name for user's email (default is "email").
        :param username: str. Column name for user's username (default is "username").
        :param password: str. Column name for user's password (default is "password").
        :param phone: str. Column name for user's phone number (default is "phone").
        :param notifications str. Column name for user's notifications (default is "notifications").
        :param friends: str. Column name for user's friends (default is "friends").
        :param privatechat: str. Column name for user's private chat messages (default is "privatechat").
        :param important: str. Column name for user's important messages (default is "important").
        """
        self.__tablename = tablename
        self.__user_id = "user_id"  # Use a static column name for user ID
        self.__password = password
        self.__username = username
        self.__fullname = fullname
        self.__email = email
        self.__phone = phone
        self.__notifications = notifications
        self.__friends = friends
        self.__privatechat = privatechat
        self.__important = important

        conn = sqlite3.connect(DB_NAME)
        # print(f"{FILE_NAME}: Opened database successfully")
        query_str = f"CREATE TABLE IF NOT EXISTS {tablename} ({self.__user_id} TEXT NOT NULL, " \
                    f"{username} TEXT NOT NULL, {password} TEXT NOT NULL, {fullname} TEXT NOT NULL, " \
                    f"{email} TEXT NOT NULL, {phone} TEXT NOT NULL, {notifications} TEXT NOT NULL, " \
                    f"{friends} TEXT NOT NULL, {privatechat} TEXT NOT NULL, {important} TEXT NOT NULL);"

        conn.execute(query_str)
        print(f"{FILE_NAME}: Table created successfully")
        conn.commit()
        conn.close()

    def __str__(self):
        """
        Returns a string representation of the Users object.
        :return: str. A string representing the table name.
        """
        return "table name is ", self.__tablename

    def validate_input(self, input_string):
        """
        This function checks if the input string contains any suspicious characters that might be used in SQL injection attacks.
        :param input_string: str. The input string to be validated.
        :return: bool. True if the input is valid, False if it contains suspicious characters.
        """
        # List of suspicious characters commonly used in SQL injection attacks
        suspicious_characters = ["'", ";", "--", "/*", "*/"]

        # Check if the input string contains any suspicious characters
        for char in suspicious_characters:
            if char in input_string:
                return False

        return True

    def insert_user(self, fullname, email, username, password, phone):
        """
        This function inserts a new user into the database.
        :param fullname: str. The full name of the user.
        :param email: str. The email address of the user.
        :param username: str. The username of the user.
        :param password: str. The password of the user.
        :param phone: str. The phone number of the user.
        :return: str. "YES" if the user is successfully inserted, "NO" otherwise.
        """

        if not self.validate_input(fullname) or not self.validate_input(email) \
                or not self.validate_input(username) or not self.validate_input(password) \
                or not self.validate_input(phone):
            print("Input contains suspicious characters. Insertion aborted.")
            return "NO"
        notification = ""
        friends = ""
        private_chat = ""
        important_msg = ""
        # print(f"{FILE_NAME}: {fullname, email, username, password, phone}")
        if not self.check_exist_username(username):  # if he doesn't exist...
            user_id = self.get_unique_id()

            conn = sqlite3.connect(DB_NAME)
            insert_query = f"INSERT INTO {self.__tablename} ({self.__user_id}, {self.__fullname}, {self.__email}, {self.__username}, {self.__password}, {self.__phone}, {self.__notifications}, {self.__friends}, {self.__privatechat}, {self.__important}) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
            conn.execute(insert_query, (user_id, fullname, email, username, password, phone, notification, friends, private_chat, important_msg))

            conn.commit()
            conn.close()
            # print(f"{FILE_NAME}: Record created successfully")
            return "YES"
        return "NO"

    def check_exist(self, username, password):
        """
        This function checks if a user exists in the database with the provided username and password.
        :param username: str. The username of the user.
        :param password: str. The password of the user.
        :return: bool. True if the user exists, False otherwise.
        """
        conn = sqlite3.connect(DB_NAME)
        # print(f"{FILE_NAME}: Opened database successfully")
        if not self.validate_input(username) or not self.validate_input(password):
            print("Input contains suspicious characters. Insertion aborted.")
            return False

        sql_query = f"SELECT * FROM {self.__tablename} WHERE {self.__username} = ? AND {self.__password} = ?"
        cursor = conn.execute(sql_query, (username, password))

        # Fetch the first row from the result set
        row = cursor.fetchone()

        if row is not None:
            return True
        conn.close()
        return False

    def check_exist_username(self, username):
        """
        This function checks if a user exists in the database with the provided username.
        :param username: str. The username of the user.
        :return: bool. True if the user exists, False otherwise.
        """
        print(f"{FILE_NAME}: in check exist username. checking if {username} exist")
        conn = sqlite3.connect(DB_NAME)
        # print(f"{FILE_NAME}: Opened database successfully")
        sql_query = f"SELECT * FROM {self.__tablename} WHERE {self.__username} = ?"
        cursor = conn.execute(sql_query, (username,))

        row = cursor.fetchone()
        if row is not None:
            return True
        conn.close()
        return False

    def get_unique_id(self):
        """
        This function generates a unique user ID.
        :return: str. The unique user ID.
        """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        while True:
            user_id = global_use_for_server.generate_id(10, "call")
            sql_query = f"SELECT user_id FROM {self.__tablename} WHERE {self.__user_id} = ?"
            cursor.execute(sql_query, (user_id,))
            row = cursor.fetchone()

            if row is None:
                conn.close()
                return user_id

        conn.close()

    def get_notifications(self, username):
        """
        This function retrieves notifications for a given user.
        :param username: str. The username of the user.
        :return: str or None. The notifications for the user, or None if no notifications found.
        """
        conn = sqlite3.connect(DB_NAME)
        # print(f"{FILE_NAME}: Opened database successfully")
        sql_query = f"SELECT {self.__notifications} FROM {self.__tablename} WHERE {self.__username} = ?"
        cursor = conn.execute(sql_query, (username,))
        row = cursor.fetchone()
        if row is not None:
            return row[0]
        conn.close()
        return None

    def get_email(self, username):
        """
        This function retrieves the email address of a given user.
        :param username: str. The username of the user.
        :return: str or None. The email address of the user, or None if not found.
        """
        conn = sqlite3.connect(DB_NAME)
        # print(f"{FILE_NAME}: Opened database successfully")
        sql_query = f"SELECT {self.__email} FROM {self.__tablename} WHERE {self.__username} = ?"
        cursor = conn.execute(sql_query, (username,))
        row = cursor.fetchone()
        if row is not None:
            return row[0]
        conn.close()
        return None

    def get_important(self, username):
        """
        This function retrieves important messages for a given user.
        :param username: str. The username of the user.
        :return: str or None. The important messages for the user, or None if not found.
        """
        conn = sqlite3.connect(DB_NAME)
        # print(f"{FILE_NAME}: Opened database successfully")
        sql_query = f"SELECT {self.__important} FROM {self.__tablename} WHERE {self.__username} = ?"
        cursor = conn.execute(sql_query, (username,))
        row = cursor.fetchone()
        if row is not None:
            return row[0]
        conn.close()
        return None

    def get_private_chat(self, username, target_username):
        """
        This function retrieves private chat messages between two users.
        :param username: str. The username of the first user.
        :param target_username: str. The username of the second user.
        :return: dict or None. The private chat messages between the users, or None if not found.
        """
        conn = sqlite3.connect(DB_NAME)
        # print(f"{FILE_NAME}: Opened database successfully")

        # Fetching the private_chats JSON string from the database
        sql_query = f"SELECT {self.__privatechat} FROM {self.__tablename} WHERE {self.__username} = ?"
        cursor = conn.execute(sql_query, (username,))
        row = cursor.fetchone()
        print(f"{FILE_NAME}: ---- row = {row}")
        if row is not None:
            try:
                private_chats_json = row[0]
                private_chats_dict = json.loads(private_chats_json)
            except:
                return None
            # Retrieving the private chat for the target user
            if target_username in private_chats_dict:
                print(f"{FILE_NAME}: in if3")
                private_chat = private_chats_dict[target_username]
                return private_chat
            else:
                print(f"{FILE_NAME}: in if4")
                return {}
        return None
        conn.close()

    def set_both_private_chat(self, self_username, target_username, message):
        """
        This function sets private chat messages between two users.
        :param self_username: str. The username of the sender.
        :param target_username: str. The username of the receiver.
        :param message: str. The message to be sent.
        :return: bool. True if the operation is successful, False otherwise.
        """
        conn = sqlite3.connect(DB_NAME)
        # print(f"{FILE_NAME}: Opened database successfully")

        # Fetching the private_chats JSON string from the database for the sender
        sql_query_sender = f"SELECT {self.__privatechat} FROM {self.__tablename} WHERE {self.__username} = ?"
        cursor_sender = conn.execute(sql_query_sender, (self_username,))
        row_sender = cursor_sender.fetchone()
        private_chats_dict_sender = {}
        print(f"{FILE_NAME}: row_sender is {row_sender}")
        if row_sender is not None:
            if row_sender[0]:  # Check if private_chats_json is not empty
                private_chats_dict_sender = json.loads(row_sender[0])
                print(private_chats_dict_sender)
            else:
                print(f"{FILE_NAME}: private_chats_json is empty for sender")

            print(f"{FILE_NAME}: private chats dict for sender is= {private_chats_dict_sender}")

            if target_username in private_chats_dict_sender:
                private_chats_dict_sender[target_username].append({"sender": self_username, "message": message})
            else:
                private_chats_dict_sender[target_username] = [{"sender": self_username, "message": message}]

            # Updating the private_chats JSON string in the database for the sender
            updated_private_chats_json_sender = json.dumps(private_chats_dict_sender)
            update_query_sender = f"UPDATE {self.__tablename} SET {self.__privatechat} = ? WHERE {self.__username} = ?"
            conn.execute(update_query_sender, (updated_private_chats_json_sender, self_username))
            conn.commit()

        # Fetching the private_chats JSON string from the database for the receiver
        sql_query_receiver = f"SELECT {self.__privatechat} FROM {self.__tablename} WHERE {self.__username} = ?"
        cursor_receiver = conn.execute(sql_query_receiver, (target_username,))
        row_receiver = cursor_receiver.fetchone()
        private_chats_dict_receiver = {}

        if row_receiver is not None:
            if row_receiver[0]:  # Check if private_chats_json is not empty
                private_chats_dict_receiver = json.loads(row_receiver[0])
                print(f"{FILE_NAME}: {private_chats_dict_receiver}")
            else:
                print(f"{FILE_NAME}: private_chats_json is empty for receiver")

            print(f"{FILE_NAME}: private chats dict for receiver is= {private_chats_dict_receiver}")

            if self_username in private_chats_dict_receiver:
                private_chats_dict_receiver[self_username].append({"sender": self_username, "message": message})
            else:
                private_chats_dict_receiver[self_username] = [{"sender": self_username, "message": message}]

            # Updating the private_chats JSON string in the database for the receiver
            updated_private_chats_json_receiver = json.dumps(private_chats_dict_receiver)
            update_query_receiver = f"UPDATE {self.__tablename} SET {self.__privatechat} = ? WHERE {self.__username} = ?"
            conn.execute(update_query_receiver, (updated_private_chats_json_receiver, target_username))
            conn.commit()

            conn.close()
            return True
        else:
            conn.close()
            return False

    def set_group_chat(self, username, sender, group, message):
        """
        This function updates the chat cell of a user with a group chat.

        Parameters:
            username (str): The username of the user whose chat cell is to be updated.
            sender (str): The username of the user sending the message.
            group (str): String containing usernames of all participants in the group, separated by commas.
            message (str): The message to be sent.

        Returns:
            bool: True if the update is successful, False otherwise.
        """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Fetching the private_chats JSON string from the database
        sql_query = f"SELECT {self.__privatechat} FROM {self.__tablename} WHERE {self.__username} = ?"
        cursor.execute(sql_query, (username,))
        row = cursor.fetchone()

        private_chats_dict = {}
        if row is not None:
            if row[0]:
                private_chats_dict = json.loads(row[0])
            else:
                print(f"{FILE_NAME}: private_chats_json is empty for receiver")

            # Update the chat for the group
            if group in private_chats_dict:
                private_chats_dict[group].append({"sender": sender, "message": message})
            else:
                private_chats_dict[group] = [{"sender": sender, "message": message}]

            # Update the private_chats JSON string in the database
            updated_private_chats_json = json.dumps(private_chats_dict)
            update_query = f"UPDATE {self.__tablename} SET {self.__privatechat} = ? WHERE {self.__username} = ?"
            cursor.execute(update_query, (updated_private_chats_json, username))
            conn.commit()
            conn.close()
        else:
            conn.close()

    def get_friends(self, username):
        """
        This function retrieves the friends of a given user.
        :param username: str. The username of the user.
        :return: str or None. The friends of the user, or None if not found.
        """
        # individually.
        conn = sqlite3.connect(DB_NAME)
        # print(f"{FILE_NAME}: Opened database successfully")
        sql_query = f"SELECT {self.__friends} FROM {self.__tablename} WHERE {self.__username} = ?"
        cursor = conn.execute(sql_query, (username,))

        row = cursor.fetchone()
        if row is not None:
            return row[0]
        conn.close()
        return None

    def get_usernames(self):
        """
        This function retrieves all usernames from the database.
        :return: str. A comma-separated string of all usernames.
        """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.execute(f"SELECT {self.__username} FROM {self.__tablename}")
        usernames = [row[0] for row in cursor.fetchall()]
        conn.close()
        return ", ".join(usernames)

    def set_notifications(self, username, new_notification):
        """
        This function sets notifications for a given user.
        :param username: str. The username of the user.
        :param new_notification: str. The new notification to be added.
        """
        conn = sqlite3.connect(DB_NAME)
        # print(f"{FILE_NAME}: Opened database successfully")
        current_notifications = self.get_notifications(username)
        if current_notifications:
            updated_notifications = current_notifications + "\n" + new_notification
        else:
            updated_notifications = new_notification

        sql_query = f"UPDATE {self.__tablename} SET {self.__notifications} = ? WHERE {self.__username} = ?"
        conn.execute(sql_query, (updated_notifications, username))
        conn.commit()
        conn.close()
        # print(f"{FILE_NAME}: Notifications updated successfully")

    def set_important(self, username, new_important):
        """
        This function sets important messages for a given user.
        :param username: str. The username of the user.
        :param new_important: str. The new important message to be added.
        """
        print(f"{FILE_NAME}: about to set important for {username}")

        conn = sqlite3.connect(DB_NAME)
        # print(f"{FILE_NAME}: Opened database successfully")
        current_important_content = self.get_important(username)
        if current_important_content:
            updated_important = current_important_content + "\n" + new_important
        else:
            updated_important = new_important

        sql_query = f"UPDATE {self.__tablename} SET {self.__important} = ? WHERE {self.__username} = ?"
        conn.execute(sql_query, (updated_important, username))
        conn.commit()
        conn.close()
        # print(f"{FILE_NAME}: Notifications updated successfully")

    def delete_notification(self, username, notification_to_delete):
        """
        This function deletes a specific notification for a given user.
        :param username: str. The username of the user.
        :param notification_to_delete: str. The notification to be deleted.
        """
        conn = sqlite3.connect(DB_NAME)
        # print(f"{FILE_NAME}: Opened database successfully")
        current_notifications = self.get_notifications(username)
        div_notifications = current_notifications.split("\n")
        updated_notifications = ""
        for per_n in div_notifications:
            if per_n != notification_to_delete:
                updated_notifications += f"{per_n}\n"
            else:
                print(f"{FILE_NAME}: you were searching for the notification {per_n}")
        sql_query = f"UPDATE {self.__tablename} SET {self.__notifications} = ? WHERE {self.__username} = ?"
        conn.execute(sql_query, (updated_notifications, username))
        conn.commit()
        conn.close()
        # print(f"{FILE_NAME}: Notifications updated successfully")

    def delete_important(self, username, important_to_delete):
        """
        This function deletes a specific important message for a given user.
        :param username: str. The username of the user.
        :param important_to_delete: str. The important message to be deleted.
        """
        print(f"{FILE_NAME}: delete important. username={username}, important_to_delete={important_to_delete}")
        conn = sqlite3.connect(DB_NAME)
        # print(f"{FILE_NAME}: Opened database successfully")
        print(f"{FILE_NAME}: before:   important is {self.get_important(username)}")
        current_important = self.get_important(username)
        div_important = current_important.split("\n")
        updated_important = ""
        for per_i in div_important:
            if per_i != important_to_delete:
                updated_important += f"{per_i}\n"
            else:
                print(f"{FILE_NAME}: you were searching for the important {per_i}")
        sql_query = f"UPDATE {self.__tablename} SET {self.__important} = ? WHERE {self.__username} = ?"
        conn.execute(sql_query, (updated_important, username))
        conn.commit()
        conn.close()
        print(f"{FILE_NAME}: after:   important is {self.get_important(username)}")

    def clear_important(self, username):
        """
        This function clears all important messages for a given user.
        :param username: str. The username of the user.
        """
        print(f"{FILE_NAME}: clear important. username={username}")
        conn = sqlite3.connect(DB_NAME)
        # print(f"{FILE_NAME}: Opened database successfully")
        updated_important = ""
        sql_query = f"UPDATE {self.__tablename} SET {self.__important} = ? WHERE {self.__username} = ?"
        conn.execute(sql_query, (updated_important, username))
        conn.commit()
        conn.close()
        print(f"{FILE_NAME}: after:   important is {self.get_important(username)}")

    def set_both_friends(self, username1, username2):
        """
        This function sets both users as friends.
        :param username1: str. The username of the first user.
        :param username2: str. The username of the second user.
        """
        # set both users friends status.
        conn = sqlite3.connect(DB_NAME)
        # print(f"{FILE_NAME}: Opened database successfully")
        current_friends_user1 = self.get_friends(username1)  # getting current friends content for username1
        current_friends_user2 = self.get_friends(username2)  # getting current friends content for username2
        # print(f"{FILE_NAME}: currently user1's friends are {current_friends_user1}")

        if current_friends_user1:
            updated_friends_user1 = current_friends_user1
            if username2 not in current_friends_user1:
                updated_friends_user1 = current_friends_user1 + "\n" + username2  # adding new friend
        else:  # user1 has no friends (now)
            updated_friends_user1 = username2  # adding new friend
        # print(f"{FILE_NAME}: now user1's friends are about to be {updated_friends_user1} ")

        sql_query = f"UPDATE {self.__tablename} SET {self.__friends} = ? WHERE {self.__username} = ?"
        conn.execute(sql_query, (updated_friends_user1, username1))

        # print(f"{FILE_NAME}: currently user2's friends are {current_friends_user2}")

        if current_friends_user2:
            updated_friends_user2 = current_friends_user2
            if username1 not in current_friends_user2:
                updated_friends_user2 = current_friends_user2 + "\n" + username1  # adding new friend
        else:  # user2 has no friends (now)
            updated_friends_user2 = username1  # adding new friend
        # print(f"{FILE_NAME}: now user1's friends are about to be {updated_friends_user2} ")

        sql_query = f"UPDATE {self.__tablename} SET {self.__friends} = ? WHERE {self.__username} = ?"
        conn.execute(sql_query, (updated_friends_user2, username2))

        conn.commit()
        conn.close()
        # print(f"{FILE_NAME}: Friends updated successfully")

    def set_group(self, username, group):
        """
        This function sets a group for a given user.
        :param username: str. The username of the user.
        :param group: list. The list of participants in the group.
        """
        print(f"{FILE_NAME}: set group. username={username}, group={group}")
        conn = sqlite3.connect(DB_NAME)
        update = None
        current = self.get_friends(username)  # current cell content.
        print(f"current is {current}")
        if current and str(group) not in current:  # not empty & the group doesn't exist yet.
            update = current + "\n" + str(group)
        else:
            update = str(group)
        print(f"\nupdate is {update}\n")
        sql_query = f"UPDATE {self.__tablename} SET {self.__friends} = ? WHERE {self.__username} = ?"
        conn.execute(sql_query, (update, username))

        conn.commit()
        conn.close()

    def delete_database(self):
        """
        This function deletes the database file.
        """
        try:
            os.remove(DB_NAME)
            print(f"{DB_NAME} deleted successfully.")
        except FileNotFoundError:
            print(f"{DB_NAME} does not exist.")

    def get_entire_database(self):
        """
        This function fetches the entire database and returns it as a list of dictionaries,
        where each dictionary represents a row in the table.
        """
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Fetch all rows from the users table
        cursor.execute(f"SELECT * FROM {self.__tablename}")
        rows = cursor.fetchall()

        # Extract column names
        cursor.execute(f"PRAGMA table_info({self.__tablename})")
        columns = [col[1] for col in cursor.fetchall()]

        # Convert rows to dictionaries
        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))

        conn.close()
        return result

    def get_data_base(self):
        """
        This function fetches the entire database and returns it as a string with aligned columns.
        """
        rows = self.get_entire_database()
        formatted_database = ""

        # Determine maximum width for each column name
        column_names = list(rows[0].keys())
        max_widths = {column_name: len(column_name) for column_name in column_names}

        for row in rows:
            for column_name, value in row.items():
                max_widths[column_name] = max(max_widths[column_name], len(str(value)))

        # Format column names
        formatted_column_names = ""
        for column_name in column_names:
            formatted_column_name = column_name.rjust(max_widths[column_name])
            formatted_column_names += formatted_column_name + "  "
        formatted_database += formatted_column_names.rstrip() + "\n"

        # Add rows
        for row in rows:
            formatted_row = ""
            for column_name, value in row.items():
                # Align the value to the right based on the maximum width of the column
                formatted_value = str(value).rjust(max_widths[column_name])
                formatted_row += formatted_value + "  "
            formatted_database += formatted_row.rstrip() + "\n"

        return formatted_database

