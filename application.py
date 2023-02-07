import logging
from telebot import TeleBot
from telebot.types import Message
import os, sys
import configparser
import mysql.connector
from mysql.connector import Error
from telethon import TelegramClient, sync, events

mydb = mysql.connector.connect(
    host="database-1.cyr0uu2os5i8.eu-west-2.rds.amazonaws.com",
    user="admin",
    passwd="BREAKEdance1",
    database="tguserscraper"
)

VALID_TOKENS = ['token1', 'token2', 'token3']

BOT_TOKEN = '6123192886:AAF0GV2cqPsUWhTGyQ_v074TkAxidzdVzSY'

cpass = configparser.RawConfigParser()
cpass.read('config.data')

try:
    api_id = cpass['cred']['id']
    api_hash = cpass['cred']['hash']
    phone = cpass['cred']['phone']
    client = TelegramClient(phone, api_id, api_hash)
except KeyError:
    os.system('cls')
    sys.exit(1)

client.connect()
if not client.is_user_authorized():
    client.send_code_request(phone)
    os.system('cls')
    client.sign_in(phone, input('[+] Enter the code: '))
os.system('cls')

print('Starting up bot...')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

bot = TeleBot("6123192886:AAF0GV2cqPsUWhTGyQ_v074TkAxidzdVzSY")

cursor = mydb.cursor(buffered=True)

# Get the number of tables
cursor = mydb.cursor()
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

# Get the number of rows in each table
result = []
for table in tables:
    table_name = table[0]
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    result.append((table_name, row_count))

print(type(result))


authorized_users = [555377662]

# Create a decorator to check if the user is authorized
def authorized(func):
    def wrapper(*args, **kwargs):
        user_id = args[0].message.from_user.id
        if user_id not in authorized_users:
            bot.send_message(chat_id=user_id, text="Unauthorized access.")
            return
        return func(*args, **kwargs)
    return wrapper

# Use the authorized decorator to decorate the handler function
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id not in authorized_users:
        bot.send_message(chat_id=message.chat.id, text="You are not authorized to use this bot.")
    else:
        bot.send_message(chat_id=message.chat.id, text="Welcome! You are now authenticated.")

@bot.message_handler(commands=['db_info'])
def tables_info(message):
    user_id = message.from_user.id
    if user_id not in authorized_users:
        bot.send_message(chat_id=message.chat.id, text="You are not authorized to use this bot.")
    else:
        response = ""
        for table_name, row_count in result:
            response += f"{table_name}: {row_count} rows\n"

    bot.send_message(chat_id=message.chat.id, text=response)

@bot.message_handler(commands=['help'])
def help(message: Message):
    user_id = message.from_user.id
    if user_id not in authorized_users:
        bot.send_message(chat_id=message.chat.id, text="You are not authorized to use this bot.")
    else:
        bot.reply_to(message, "Available commands:\n/groups + Telegram username/ID - Atgriezt grupas kurās bija lietotājs \n/text + Telegram ID - Atgriezt visus ierakstus kurus bija atstājis lietotājs,\n/db_info informācija par mūsu datubāzi")

@bot.message_handler(commands=['info'])
def info(message: Message):
    user_id = message.from_user.id
    if user_id not in authorized_users:
        bot.send_message(chat_id=message.chat.id, text="You are not authorized to use this bot.")
    else:
        bot.reply_to(message, "I am a Telegram Bot. I can do many things. Try me!")

@bot.message_handler(commands=['text'])
def query_handler(message):
    user_id = message.from_user.id
    if user_id not in authorized_users:
        bot.send_message(chat_id=message.chat.id, text="You are not authorized to use this bot.")
    else:
        input_text = str(message.text.replace("/text", "").strip())
        print(input_text)
        try:
            connection = mysql.connector.connect(
                host="database-1.cyr0uu2os5i8.eu-west-2.rds.amazonaws.com",
                user="admin",
                passwd="BREAKEdance1",
                database="tguserscraper"
            )
            cursor = connection.cursor()
            query = "SELECT * FROM tguserscraper.telegram_scraper_text WHERE tele_sender LIKE %s"
            cursor.execute(query, ('%' + input_text + '%',))
            result = cursor.fetchall()
            print(result)
            output = "Results:\n"
            for row in result:
                output += "👥 GRUPA: {}\n".format(row[1])
                output += "🆔 USER ID: {}\n".format(row[2])
                output += " 🔤 TEXT: {}\n\n".format(row[3])
                output += " DATUMS: {}\n\n".format(row[4])
            bot.reply_to(message, output)
        except Error as e:
            bot.reply_to(message, "Error: {}".format(e))
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()

@bot.message_handler(commands=['groups'])
def query_handler(message):
    user_id = message.from_user.id
    if user_id not in authorized_users:
        bot.send_message(chat_id=message.chat.id, text="You are not authorized to use this bot.")
    else:
        input_text = message.text.replace("/groups", "").strip()
        try:
            connection = mysql.connector.connect(
                host="database-1.cyr0uu2os5i8.eu-west-2.rds.amazonaws.com",
                user="admin",
                passwd="BREAKEdance1",
                database="tguserscraper"
            )
            cursor = connection.cursor()
            query = "SELECT * FROM tguserscraper.telegram_scraper_test WHERE username LIKE %s"
            cursor.execute(query, (input_text,))
            print(query, (input_text,))
            result = cursor.fetchall()
            if not result:
                # Second query
                query = "SELECT * FROM tguserscraper.telegram_scraper_test WHERE user_id LIKE %s"
                cursor.execute(query, (input_text,))
                result = cursor.fetchall()
            output = "Results:\n"
            for row in result:
                output += "👤 USERNAME: {}\n".format(row[1])
                output += "🆔 USER ID: {}\n".format(row[2])
                output += "🔤 NAME: {}\n".format(row[3])
                output += "👥 GROUP NAME: {}\n".format(row[4])
                output += "🆔 GROUP ID: {}\n\n".format(row[6])
            bot.reply_to(message, output)
        except Error as e:
            bot.reply_to(message, "Error: {}".format(e))
        finally:
            if (connection.is_connected()):
                cursor.close()
                connection.close()

while True:
    try:
        bot.polling()
    except Exception as e:
        # Handle exceptions and restart the loop
        print(e)
