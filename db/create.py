import sqlite3 as sq

with sq.connect('db/database.db') as con:
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS files(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name varchar,
                format varchar,
                data LargeBinary,
                user_id integer, 
                user_name varchar)''')