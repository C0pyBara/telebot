import psycopg2
import telebot
from configparser import ConfigParser

# Чтение конфигурационного файла
config = ConfigParser()
config.read('config.ini')

# Подключение к базе данных PostgreSQL
conn = psycopg2.connect(
    dbname=config['postgresql']['dbname'],
    user=config['postgresql']['user'],
    password=config['postgresql']['password'],
    host=config['postgresql']['host'],
    port=config['postgresql']['port']
)
cur = conn.cursor()

# Создание таблицы для задач, если она ещё не существует
cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id SERIAL PRIMARY KEY,
        task TEXT NOT NULL
    )
""")
conn.commit()

bot = telebot.TeleBot(config['telegram']['token'])

# Функция обработки команды /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я бот для управления задачами. Используй /add для добавления задачи и /list для просмотра списка задач.")

# Функция обработки команды /add
@bot.message_handler(commands=['add'])
def add_task(message):
    task = ' '.join(message.text.split()[1:])  # Получаем текст после команды
    cur.execute("INSERT INTO tasks (task) VALUES (%s)", (task,))
    conn.commit()
    bot.send_message(message.chat.id, "Задача успешно добавлена!")

# Функция обработки команды /list
@bot.message_handler(commands=['list'])
def list_tasks(message):
    cur.execute("SELECT task FROM tasks")
    tasks = cur.fetchall()
    if tasks:
        task_list = '\n'.join([f"{index + 1}. {task[0]}" for index, task in enumerate(tasks)])
        bot.send_message(message.chat.id, f"Ваши задачи:\n{task_list}")
    else:
        bot.send_message(message.chat.id, "У вас пока нет задач.")

# Функция для обработки неизвестных команд
@bot.message_handler(func=lambda message: True)
def unknown(message):
    bot.send_message(message.chat.id, "Извините, я не понимаю эту команду.")

bot.polling()