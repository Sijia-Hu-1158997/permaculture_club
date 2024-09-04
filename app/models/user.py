import random
import string
from flask import g
from flask_hashing import Hashing
import datetime


class UserModel:
    def __init__(self):
        self.conn = g.db_conn
        self.hashing = Hashing()

    def generate_salt(self, length=10):
        characters = string.ascii_letters + string.digits
        random_string = "".join(random.choices(characters, k=length))
        return random_string

    # Register flow
    # Step 1: fill in username(uniq) email(uniq) password;
    # Step 2: fill in first_name last_name address phone_number birth_date etc.;
    # Step 3: select a plan to subscription and pay monthly $200 & annually $2000;
    # Step 4: finished all registration process and navigate to the home page;
    def register_user(self, data: dict):
        # step 1
        sql = """
        INSERT INTO users
        (username, email, password, onboarding)
        VALUES (%s, %s, %s, %s);
        """
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        onboarding = 1

        salt = self.generate_salt()
        hash_password = f"{self.hashing.hash_value(password, salt)}:{salt}"
        cur = self.conn.cursor()
        cur.execute(sql, (username, email, hash_password, onboarding))
        self.conn.commit()
        cur.close()

    def admin_register_user(self, data: dict):
        # step 1
        sql = """
        INSERT INTO users
        (username, email, password, role, onboarding)
        VALUES (%s, %s, %s, %s, %s);
        """
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")
        onboarding = 1

        salt = self.generate_salt()
        hash_password = f"{self.hashing.hash_value(password, salt)}:{salt}"

        cur = self.conn.cursor()
        cur.execute(sql, (username, email, hash_password, role, onboarding))
        self.conn.commit()
        cur.close()

    def update_user_info(self, user_id, data):
        valid_keys = {
            "username",
            "password",
            "role",
            "title",
            "first_name",
            "last_name",
            "position",
            "phone",
            "address",
            "date_of_birth",
            "profile_image",
            "permaculture_experience",
            "instructor_profile",
            "is_deleted",
            "subscription",
            "started_at",
            "expired_at",
            "onboarding",
        }
        data = {
            k: v
            for k, v in data.items()
            if k in valid_keys and v is not None and k not in ["email", "id"]
        }

        # If no valid data to update, return early to avoid executing an empty update
        if not data:
            print("No valid data provided for update.")
            return
        # Build the SQL dynamically based on the data provided
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        values = list(data.values())

        # Include user_id at the end for the WHERE clause
        values.append(user_id)
        print(set_clause, values)
        sql = f"""
        UPDATE users
        SET {set_clause}
        WHERE id = %s;
        """

        cur = self.conn.cursor()
        cur.execute(sql, tuple(values))
        self.conn.commit()
        cur.close()

    def get_user_by_field(self, field_name, field_value):
        """
        Fetch a user by a specific field name and value.

        :param field_name: The name of the field to query (e.g., 'email' or 'username' or 'id').
        :param field_value: The value of the field to query.
        :return: A dictionary of the user's data if found, None otherwise.
        """
        if field_name not in ["email", "username", "id"]:
            raise ValueError("Invalid field name. Allowed fields: 'email', 'username'")

        sql = f"SELECT * FROM users WHERE {field_name} = %s"
        with self.conn.cursor() as cur:
            cur.execute(sql, (field_value,))
            user_tuple = cur.fetchone()

            if user_tuple:
                columns = [desc[0] for desc in cur.description]
                user = dict(zip(columns, user_tuple))
                return user
            else:
                return None

    def get_instructors(self):

        sql = f"SELECT * FROM users WHERE role = 'instructor'"
        with self.conn.cursor() as cur:
            cur.execute(sql)
            users_tuples = cur.fetchall()

            users = []
            for user_tuple in users_tuples:
                columns = [desc[0] for desc in cur.description]
                user = dict(zip(columns, user_tuple))
                users.append(user)

            return users

    def get_instructors_by_id(self, user_id):

        sql = "SELECT * FROM users WHERE id = %s AND role = 'instructor'"
        with self.conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            instructor_tuple = cur.fetchall()

            if instructor_tuple:
                columns = [desc[0] for desc in cur.description]
                instructor = dict(zip(columns, instructor_tuple))
                return instructor
            else:
                return None

    def check_password(self, username, password):
        sql = "SELECT * FROM users WHERE username = %s"
        cur = self.conn.cursor()
        cur.execute(sql, (username,))
        user_tuple = cur.fetchone()
        if cur.description and user_tuple:
            columns = [desc[0] for desc in cur.description]
            user = dict(zip(columns, user_tuple))
            if user:
                hash_password, salt = user["password"].split(":")
                if self.hashing.check_value(hash_password, password, salt):
                    return user
                else:
                    # add
                    print("Stored password format is incorrect.")
            else:
                # add
                print("User not found.")
        return None



    def get_users(self, query=None):
        sql = "SELECT * FROM users"
        params = []

        search_columns = ["first_name", "last_name", "email", "username", "phone"]

        if query:
            query_conditions = [f"{col} LIKE %s" for col in search_columns]
            sql += " WHERE (" + " OR ".join(query_conditions) + ")"

            params = ["%" + query + "%"] * len(query_conditions)

        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            users = cur.fetchall() or []

            if cur.description:
                columns = [desc[0] for desc in cur.description]
                users_dicts = [dict(zip(columns, user)) for user in users]
            else:
                users_dicts = []

        return users_dicts


    def delete_user(self, user_id):
        sql = "DELETE FROM users WHERE id = %s"
        cur = self.conn.cursor()
        cur.execute(sql, (user_id,))
        self.conn.commit()
        cur.close()

    def update_password(self, user_id, password):
        sql = "UPDATE users SET password = %s WHERE id = %s"
        salt = self.generate_salt()
        hash_password = f"{self.hashing.hash_value(password, salt)}:{salt}"
        cur = self.conn.cursor()
        cur.execute(sql, (hash_password, user_id))
        self.conn.commit()
        cur.close()

    def update_profile_img(self,user_id,profile_image):
        sql = "UPDATE users SET profile_image = %s WHERE id = %s"
        cur = self.conn.cursor()
        cur.execute(sql, (profile_image, user_id))
        self.conn.commit()
        cur.close()


    def get_feedback(self, query=None):
        sql = "SELECT * FROM feedback"
        params = []

        search_columns = ["title", "content", "published_at"]

        if query:
            query_conditions = [f"{col} LIKE %s" for col in search_columns]
            sql += " WHERE (" + " OR ".join(query_conditions) + ")"

            params = ["%" + query + "%"] * len(query_conditions)

        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            users = cur.fetchall() or []

            if cur.description:
                columns = [desc[0] for desc in cur.description]
                users_dicts = [dict(zip(columns, user)) for user in users]
            else:
                users_dicts = []

        return users_dicts
    
    def add_feedback(self, data: dict):
        sql = """
        INSERT INTO feedback (title, content, published_at, feedback_user_id)
        VALUES (%s, %s, %s, %s);
        """
        title = data.get("title")
        content = data.get("content")
        published_at = datetime.datetime.now().date()
        feedback_user_id = data.get("feedback_user_id")
        
        cur = self.conn.cursor()
        cur.execute(sql, (title, content, published_at,feedback_user_id))
        self.conn.commit()
        cur.close()