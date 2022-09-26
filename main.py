import sqlite3 as sql
from os import getcwd, getenv
from dotenv import load_dotenv
import telebot

PATH = getcwd()
DB_PATH = PATH + "/users.db"
load_dotenv(PATH + '/.env')
TOKEN = getenv('TG_TOKEN')


def defence(username, chatID):
    username.replace("'", "")
    username.replace('"', "")
    return username, int(chatID)

def get_users(chatid):
    db = sql.connect(DB_PATH)
    with db:
        c = db.cursor()
        c.execute("SELECT username FROM users WHERE chatID = ?", [int(chatid)])
        users_list = [x[0] for x in c.fetchall()]
        return users_list


def check_user(username, chatid):
    username = f"@{username}"
    username, chatid = defence(username, chatid)
    with sql.connect(DB_PATH) as db:
        c = db.cursor()
        c.execute(
            "SELECT username FROM users WHERE username = ? AND chatID = ?", (username, chatid))
        user = c.fetchone()
        if user is None:
            c.execute(
                'INSERT INTO users (username, chatID) VALUES (?, ?)', (username, chatid))
            db.commit()

def delete_user(username, chatid):
    username = f"@{username}"
    username, chatid = defence(username, chatid)
    with sql.connect(DB_PATH) as db:
        c = db.cursor()
        c.execute(
            "SELECT username FROM users WHERE username = ? AND chatID = ?", (username, chatid))
        user = c.fetchone()
        if user is not None:
            c.execute("DELETE FROM users WHERE username = ? AND chatID = ?", (username, chatid))
            db.commit()


def startbot():
    bot = telebot.TeleBot(TOKEN)

    @ bot.message_handler(commands=['join'])
    def add_user(message):
        check_user(message.from_user.username, message.chat.id)

    @ bot.message_handler(commands=['ping'])
    def ping(message):
        users_list = get_users(message.chat.id)
        all_users = ""
        for user in users_list:
            all_users += user
        if (len(all_users)) > 0:
            bot.send_message(message.chat.id, all_users)

    @ bot.message_handler(commands=['help'])
    def help_out(message):
        txt = "/join for join and /ping for ping"
        bot.send_message(message.chat.id, txt)

    @ bot.message_handler(commands=['delete'])
    def delete_user_request(message):
        username = message.from_user.username
        userid = message.chat.id
        delete_user(username, userid)


    bot.polling(none_stop=True)


if __name__ == "__main__":
    db = sql.connect(DB_PATH)
    with db:
        c = db.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, chatID INT)")
        db.commit()
    startbot()
