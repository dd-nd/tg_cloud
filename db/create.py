import sqlite3 as sq

with sq.connect('db/database.db') as con:
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name varchar)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS genres(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name varchar)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS types(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name varchar)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS statuses(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name varchar)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS contents(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                name varchar, 
                genre_id INTEGER, 
                type_id INTEGER, 
                status_id INTEGER,
                user_id INTEGER, 
                FOREIGN KEY (genre_id) references genres(id),
                FOREIGN KEY (type_id) references types(id),
                FOREIGN KEY (status_id) references statuses(id),
                FOREIGN KEY (user_id) references users(id))''')

    cur.execute('''INSERT INTO genres (name) VALUES ('Боевик'), ('Комедия'), ('Драма'), 
                                                    ('Мелодрама'), ('Триллер'), ('Научная фантастика'), 
                                                    ('Фэнтези'), ('Ужасы'), ('Приключения'), ('Другое')''')
    cur.execute('''INSERT INTO types (name) VALUES ('Фильм'), ('Мультфильм'), ('Аниме')''')
    cur.execute('''INSERT INTO statuses (name) VALUES ('Планирую'), ('В процессе'), ('Смотрел')''')