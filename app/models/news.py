import random
import string
from flask import g
from flask_hashing import Hashing
import datetime

class NewsModel:
    def __init__(self):
        self.conn = g.db_conn
        self.hashing = Hashing()

    def add_news(self, data: dict):
        sql = """
        INSERT INTO news (title, content, status, published_at, created_at, updated_at, author_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        title = data.get("title")
        content = data.get("content")
        status = "draft"
        published_at = datetime.datetime.now().date()
        created_at = datetime.datetime.now()
        updated_at = datetime.datetime.now()
        author_id = data.get("author_id")
        
        cur = self.conn.cursor()
        cur.execute(sql, (title, content, status, published_at, created_at, updated_at, author_id))
        self.conn.commit()
        cur.close()

    def get_news(self, query=None):
        sql = """SELECT 
                    news.id,
                    news.title,
                    news.author_id,
                    CONCAT(users.first_name, ' ', users.last_name) AS author_name,
                    news.content,
                    news.status,
                    news.published_at,
                    news.created_at,
                    news.updated_at
                FROM news
                LEFT JOIN users ON news.author_id = users.id
            """
        params = []

        search_columns = ["news.title", "news.content", "news.status"]

        if query:
            query_conditions = [f"{col} LIKE %s" for col in search_columns]
            sql += " WHERE (" + " OR ".join(query_conditions) + ")"

            params = ["%" + query + "%"] * len(query_conditions)

        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            news = cur.fetchall() or []

            if cur.description:
                columns = [desc[0] for desc in cur.description]
                news_dicts = [dict(zip(columns, n)) for n in news]
            else:
                news_dicts = []

        return news_dicts
    
    def get_news_by_id(self, id):
        sql = "SELECT * FROM news WHERE id = %s"
        cur = self.conn.cursor()
        cur.execute(sql, (id,))
        news_tuple = cur.fetchone()
        if cur.description and news_tuple:
            columns = [desc[0] for desc in cur.description]
            news = dict(zip(columns, news_tuple))
            return news
        else:
            return None
        

    def view_news(self, query=None):
        sql = "SELECT * FROM news WHERE status = 'published'"

        params = []

        search_columns = ["title", "content"]

        if query:
            query_conditions = [f"{col} LIKE %s" for col in search_columns]
            sql += " WHERE (" + " OR ".join(query_conditions) + ")"

            params = ["%" + query + "%"] * len(query_conditions)

        with self.conn.cursor() as cur:
            cur.execute(sql, params)
            news = cur.fetchall() or []

            if cur.description:
                columns = [desc[0] for desc in cur.description]
                news_dicts = [dict(zip(columns, n)) for n in news]
            else:
                news_dicts = []

        return news_dicts
    
    def get_news_by_id(self, id):
        sql = "SELECT * FROM news WHERE id = %s"
        cur = self.conn.cursor()
        cur.execute(sql, (id,))
        news_tuple = cur.fetchone()
        if cur.description and news_tuple:
            columns = [desc[0] for desc in cur.description]
            news = dict(zip(columns, news_tuple))
            return news
        else:
            return None
    
    
    def update_news(self, id, data):
        valid_keys = {
            "title",
            "author_id",
            "content",
            "status",
        }
        data = {
            k: v
            for k, v in data.items()
            if k in valid_keys and v is not None and k not in ["id"]
        }

        if not data:
            print("No valid data provided for update.")
            return
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        values = list(data.values())

        values.append(id)
        print(set_clause, values)
        sql = f"""
        UPDATE news
        SET {set_clause}
        WHERE id = %s;
        """

        cur = self.conn.cursor()
        cur.execute(sql, tuple(values))
        self.conn.commit()
        cur.close()


    def delete_news(self, user_id):
        sql = "DELETE FROM news WHERE id = %s"
        cur = self.conn.cursor()
        cur.execute(sql, (user_id,))
        self.conn.commit()
        cur.close()