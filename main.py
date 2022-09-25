import sqlite3 as sql
from os import getcwd, getenv
from dotenv import load_dotenv
import telebot

PATH = getcwd()
DB_PATH = PATH + "/users.db"
load_dotenv(PATH + '/.env')
TOKEN = getenv('TG_TOKEN')


def get_users():
    db = sql.connect(DB_PATH)
    with db:
        c = db.cursor()
        c.execute("SELECT username FROM users")
        users_list = [x[0] for x in c.fetchall()]
        return users_list


def check_user(username):
    username = f"@{username}"
    db = sql.connect(DB_PATH)
    with db:
        c = db.cursor()
        c.execute("SELECT username FROM users WHERE username = ?", [username])
        user = c.fetchone()
        if user is None:
            c.execute('INSERT INTO users (username) VALUES (?)', [username])
            db.commit()


def startbot():
    bot = telebot.TeleBot(TOKEN)

    @ bot.message_handler(commands=['join'])
    def add_user(message):
        check_user(message.from_user.username)

    @ bot.message_handler(commands=['ping'])
    def ping(message):
        users_list = get_users()
        all_users = ""
        for user in users_list:
            all_users += user
        bot.send_message(message.chat.id, all_users)

    @ bot.message_handler(commands=['help'])
    def help_out(message):
        txt = "/join for join and /ping for ping"
        bot.send_message(message.chat.id, txt)

    bot.polling(none_stop=True)


if __name__ == "__main__":
    db = sql.connect(DB_PATH)
    with db:
        c = db.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT UNIQUE)")
        db.commit()
    startbot()
