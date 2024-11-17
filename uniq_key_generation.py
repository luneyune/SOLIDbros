import bcrypt
import sqlite3
import random
from sqlite_setup import *

def get_hashed_pasword(plain_text_password):
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())

db_setup()

symbol_numbers = [i for i in range(65, 91)] + [i for i in range(97, 123)]
symbols = [chr(i) for i in symbol_numbers]

key = "".join([random.choice(symbols) for i in range(32)])
print(key)

hashed_key = get_hashed_pasword(key)

with sqlite3.connect("users.db") as connection:
    cursor = connection.cursor()
    cursor.execute("INSERT INTO TokenKeys (x_api_key) VALUES (?)", (hashed_key, ))
    connection.commit()
