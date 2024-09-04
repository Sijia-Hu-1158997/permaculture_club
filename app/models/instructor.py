import random
import string
from flask import g
from flask_hashing import Hashing


class InstructorModel:
    def __init__(self):
        self.conn = g.db_conn
        self.hashing = Hashing()

    def get_all_Instructors(self, query=None):
        sql = "SELECT * FROM users where role='instructor'"
        params = []

        search_columns = ["username", "first_name", "last_name"]

        if query:
            query_conditions = [f"{col} LIKE %s" for col in search_columns]
            sql += " and (" + " OR ".join(query_conditions) + ")"

            params = ["%" + query + "%"] * len(query_conditions)

        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            items = cur.fetchall() or []

            if cur.description:
                columns = [desc[0] for desc in cur.description]
                items_dicts = [dict(zip(columns, item)) for item in items]
            else:
                items_dicts = []

        return items_dicts

    def get_instructor_by_id(self, id):
        sql = "SELECT * FROM users WHERE id = %s"
        cur = self.conn.cursor()
        cur.execute(sql, (id,))
        instructor_tuple = cur.fetchone()
        if cur.description and instructor_tuple:
            columns = [desc[0] for desc in cur.description]
            instructor = dict(zip(columns, instructor_tuple))
            return instructor
        else:
            return None

