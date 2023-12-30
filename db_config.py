import sqlite3

db = sqlite3.connect('coins.db')

#cursor obj
cursor = db.cursor()

class UserDB:
    def __init__(self, username: str = None, uid: int = None, coins: int = None, last_played: int = None) -> None:
        self.username = username
        self.uid = uid
        self.coins = coins
        self.last_played = last_played
    
    def create_table(self):
        cursor.execute("""
        CREATE TABLE users (
            db_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            user_id INTEGER NOT NULL UNIQUE,
            coins INTEGER NOT NULL,
            last_ran INTEGER NOT NULL
        );
        """)
    
    def delete_table(self):
        cursor.execute("DROP TABLE users;")
    
    def get_table_columns(self):
        data = cursor.execute('SELECT * FROM users;')
        for columns in data.description:
            print(columns)

    def insert_user(self):
        cursor.execute(f"INSERT INTO users (username, user_id, coins, last_ran) VALUES ('{self.username}', '{self.uid}', '{self.coins}', '{self.last_played}')")
        db.commit()
    
    def get_rows(self):
        cursor.execute("SELECT * FROM users;")
        rows = cursor.fetchall()
        return rows

    def select_user(self):
        cursor.execute(f"SELECT * FROM users WHERE user_id = ?;", (self.uid,))
        row = cursor.fetchall()
        return row

    def update_coin_count(self):
        cursor.execute("SELECT coins FROM users WHERE user_id = ?;", (self.uid,))
        value = cursor.fetchall()[0]
        (coins,) = value
        new_coins = int(coins) + 100
        cursor.execute("UPDATE users SET coins = ? where user_id = ?", (new_coins, self.uid,))
        db.commit()
    
    def update_timestamp(self):
        cursor.execute("UPDATE users SET last_ran = ? where user_id = ?", (self.last_played, self.uid,))
        db.commit()
    
    def update_username(self):
        cursor.execute("UPDATE users SET username = ? where user_id = ?", (self.username, self.uid,))
        db.commit()
    

