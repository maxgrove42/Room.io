from src.config import Config
import pymysql.cursors

configuration = Config()


def get_db_connection():
    return pymysql.connect(
        host=configuration.db_host,
        user=configuration.db_user,
        password=configuration.db_password,
        db=configuration.db_name,
        charset=configuration.db_charset,
        cursorclass=pymysql.cursors.DictCursor
    )


def query_db(query, args=(), one_column=False):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, args)
            conn.commit()  # account for insertions and deletions
            result = cursor.fetchone() if one_column else cursor.fetchall()
            return result
    finally:
        conn.close()
