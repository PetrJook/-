import telebot
from telebot import types
import psycopg2
from config import host, user, password, db_name


conn = psycopg2.connect(
    host = host,
    user = user,
    password = password,
    database = db_name
)
base_date = '06-12-21' # this has to be any past monday of the upper week
cur = conn.cursor()
DAYS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница"]

def get(day):
    cur.execute(f"""
    SELECT name, full_name, day, room_numb, start_time
    FROM timetable
    INNER JOIN subject on subject.subject_id = timetable.fk_subject_id
    INNER JOIN teachers on teacher.teacher_id = subject.fk_teacher_id
    WHERE 
        CASE WHEN (current_date - date '{base_date}') % 14 < 7
            THEN day < 7
            ELSE day > 7
        END
    ORDER BY day ASC, start_time ASC 
                """)
    data = cur.fetchall()
    structured = {x: [[y[0], y[1], y[3], y[4]] for y in data if y[2] % 7 == x] for x in range(1, 6)}
    text = DAYS[day-1] + '\n' + '-'*20 + '\n'
    for i in structured[day]:
        for j in i:
            text += f"<{j}> "
        text += '\n\n'
    text += '-'*20
    return text

def full_week(current_week):
    if current_week == True:
        c1 = '<'
        c2 = '>'
    else:
        c1 = '>'
        c2 = '<'
    cur.execute(f"""
        SELECT name, full_name, day, room_numb, start_time
        FROM timetable
        INNER JOIN subject on subject.subject_id = timetable.fk_subject_id
        INNER JOIN teachers on teacher.teacher_id = subject.fk_teacher_id
        WHERE 
            CASE WHEN (current_date - date '{base_date}') % 14 < 7
                THEN day {c1} 7
                ELSE day {c2} 7
            END
        ORDER BY day ASC, start_time ASC 
                    """)

    data = cur.fetchall()
    structured = {x: [[y[0], y[1], y[3], y[4]] for y in data if y[2] % 7 == x] for x in range(1, 6)}
    text = ''
    for i in range(1,6):
        text += DAYS[i-1]
        text += '\n' + '-'*20 + '\n'
        for j in structured[i]:
            for k in j:
                text += f'<{k}> '
            text += '\n\n'
        text += '-'*20 + '\n'
    return text

def what_week():
    cur.execute(
        """SELECT (current_date - date '06-12-2021') % 14 < 7 """
    )
    res = (cur.fetchone())
    if res[0] == True:
        return 'Сейчас верхняя неделя'
    if res[0] == False:
        return 'Сейчас нижняя неделя'

token = "5052243713:AAHsIb79X1uEItYmCeSM3HhSEIAQXXLr-X0"
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row("Понедельник", "Вторник", "Среда", "Четверг")
    keyboard.row("Пятница", "Расписание на текущую неделю", "Расписание на следующую неделю", "/help")
    bot.send_message(message.chat.id, 'Для получения информации о доступных функциях напишите /help', reply_markup=keyboard)

@bot.message_handler(commands=['help'])
def start_message(message):
    bot.send_message(message.chat.id,
'Данный бот поможет вам получить актуальное расписание занятий для группы БФИ2102\n\
Команды:\n/week - узнайте, какая в данных момент неделя - верхняя или нижняя.\n\
/mtuci - Получите ссылку на официальный сайт МТУСИ.\n\
/start - используйте эту комманду, чтобы отобразить клавиши управления. С их помощью вы сможете увидеть расписание.')

@bot.message_handler(commands=['week'])
def start_message(message):
    bot.send_message(message.chat.id, what_week())

@bot.message_handler(commands=['mtuci'])
def start_message(message):
    bot.send_message(message.chat.id, 'https://mtuci.ru/')

@bot.message_handler(content_types=['text'])
def answer(message):
    if message.text.lower() == "понедельник":
        bot.send_message(message.chat.id, get(1))
    elif message.text.lower() == "вторник":
        bot.send_message(message.chat.id, get(2))
    elif message.text.lower() == "среда":
        bot.send_message(message.chat.id, get(3))
    elif message.text.lower() == "четверг":
        bot.send_message(message.chat.id, get(4))
    elif message.text.lower() == "пятница":
        bot.send_message(message.chat.id, get(5))
    elif message.text.lower() == "расписание на текущую неделю":
        bot.send_message(message.chat.id, full_week(True))
    elif message.text.lower() == "расписание на следующую неделю":
        bot.send_message(message.chat.id, full_week(False))
    else:
        bot.send_message(message.chat.id, "Извините, я Вас не понял")

if __name__ == '__main__':
    bot.polling()
cur.close()
conn.close()
