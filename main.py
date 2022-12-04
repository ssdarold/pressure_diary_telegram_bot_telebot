import telebot
import sqlite3
import datetime
import os
import time
import config

os.environ["TZ"] = "Europe/Moscow"
time.tzset()

# Создаем базу

db = sqlite3.connect('pressure_diary.db', check_same_thread=False)

cursor = db.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS pressure (
    up_pressure, down_pressure, pulse, date, time, user
)""")

db.commit()

# Начинаем создавать бота

token = config.TOKEN
bot = telebot.TeleBot(token)


# Показываем всё, что добавлено
@bot.message_handler(commands=['show'])
def show_result(message):
  cursor.execute("SELECT date FROM pressure WHERE user = ? ORDER BY date", (message.from_user.username,))
  rows = cursor.fetchall()
  full_res = []
  dates = []

  for row in rows:
    dates.append(row[0])

  # sort_dates = [datetime.datetime.strptime(ts, "%d.%m.%Y") for ts in dates]
  # sort_dates.sort()
  # sorteddates = [datetime.datetime.strftime(ts, "%d.%m.%Y") for ts in sort_dates]

  res_day = set(dates)
  sorted(res_day, key=lambda x: datetime.datetime.strptime(x, "%d.%m.%Y").strftime("%d.%m.%Y"))

  for day in res_day:
    full_res.append(day)
    full_res.append("""
    """)
    cursor.execute("SELECT up_pressure, down_pressure, pulse, time, user FROM pressure WHERE date = ? AND user = ?", (day, message.from_user.username))
    res_list = cursor.fetchall()

    for res in res_list:
      full_res.append(f"{res[3]} Давление: {res[0]} на {res[1]}. Пульс: {res[2]}")

    full_res.append("""-------------
    
    """)
    
  bot.send_message(message.chat.id, '\n'.join(map(str, full_res)))


@bot.message_handler(commands=['start'])
def start_message(message):
  bot.send_message(message.chat.id, """Привет! 
  Этот бот поможет вам вести дневник вашего артериального давления.
  
  Для начала просто напишите боту значения измеренного давления - сначала верхнее, затем через пробел - нижнее, затем так же через пробел - пульс.
  
  Пример - 120 80 96.
  
  Бот примет значения и сохранит их.
  
  Для того, чтобы прсмотреть все сохраненные значения за всё время, воспользуйтесь командой /show.
  
  Для того, чтобы удалить все заданные ранее значения, воспользуйтесь командой /delete""")

@bot.message_handler(content_types=["text"])
def GetPressure(message):
    info = message.text
    res = info.split()
    up_pressure = res[0]
    down_pressure = res[1]
    pulse = res[2]
    username = message.from_user.username
    date = datetime.datetime.today()
    time = date.strftime('%H:%M')
    day = date.strftime('%d.%m.%Y')

    cursor.execute("INSERT INTO pressure(up_pressure, down_pressure, pulse, date, time, user) VALUES (?, ?, ?, ?, ?, ?)", (up_pressure, down_pressure, pulse, day, time, username))
    db.commit()

    bot.send_message(message.chat.id, f'Успешно записано! Давление {up_pressure} на {down_pressure}, пульс {pulse}. Зафиксировано {day} в {time} для пользователя {username}')


if __name__ == '__main__':
     bot.infinity_polling()