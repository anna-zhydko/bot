import telebot
from telebot import types
import requests
import mysql.connector
from mysql.connector import Error
from bs4 import BeautifulSoup as bs
from googletrans import Translator
from langdetect import detect


#bot = telebot.TeleBot('token')


@bot.message_handler(commands=['start'])
def start(message):
    user = bot.get_chat_member(message.chat.id, message.from_user.id)  # get user information
#     connection = create_connection('localhost', 'root', 'toor', 'Users')  # connection to DB "Users", MySQL
#     create_tbl_users = (
#         "CREATE TABLE Information ("
#         "User_id VARCHAR(15) NOT NULL,"
#         "First_name VARCHAR(50) NOT NULL,"
#         "Lang_code VARCHAR(10) NOT NULL,"
#         "Status VARCHAR(15) NOT NULL)"
#     )

#     # make_query(connection, create_tbl_users, 'CREATE TABLE USERS') # Creates table users. (Already exists)
#     insert_user = (
#         "INSERT INTO Information "
#         "(User_id, First_name, Lang_code, Status) "
#         "VALUES (%s, %s, %s, %s)"
#     )
#     data_users = (user.user.id, user.user.first_name, user.user.language_code, user.status)  # values to past
#     make_query(connection, insert_user, 'INSERT INTO INFORMATION', data_users)
    source_markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)  # virtual Keyboard
    source_markup_btn1 = types.KeyboardButton('/help')
    source_markup.add(source_markup_btn1)
    bot.send_message(message.chat.id, 'Добро пожаловать! Меня зовут Harry Potter Wiki. '
                                      'Вы можете спросить любую вещь о Вселенной '
                                      'Гарри Поттера, и я расскажу, что знаю об этом. '
                                      'Попробуйте "Лукотрус", "Гиппогриф" или же "Ньют Саламандер " '
                                      'Очень важно писать на украинском или русском языке. '
                                      , reply_markup=source_markup)


@bot.message_handler(commands=['help'])
def help_(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Моя цель помогать Вам найти информацию о существах, волшебниках или волшенбниц,'
                              ' а также о создателях Поттерианы. Очень важно, чтобы Вы писали без ошибок '
                              'на украинском или русском языке. ')


# Handler search-word from user
@bot.message_handler(content_types=['text'])
def chat_message(message):
    try:
        text = message.text
        chat_id = message.chat.id
        translator = Translator()
        if detect(text) == 'ru':
            search = text.title()
        else:
            search = translator.translate(text, dest='ru').text.title()  # Sensitive to character case
        # link to harry potter fandom where we start searching
        url = 'https://harrypotter.fandom.com/ru/wiki/' \
              '%D0%A1%D0%BB%D1%83%D0%B6%D0%B5%D0%B1%D0%BD%D0%B0%D1%8F:Search?query='
        response = requests.get(url, params={'query': search})
        soup = bs(response.text, 'html.parser')
        page_link = soup.find(class_='result-link').get(
            'href')  # Page_link - where information about "search" is stored
        response_page = requests.get(page_link)
        page = bs(response_page.text, 'html.parser')
        try:
            bot.send_photo(chat_id, get_photo(page))
            if get_info(page): bot.send_message(chat_id, get_info(page))
        except AttributeError:
            # receive information about couple of "search"
            info = page.find('div', id='mw-content-text').text.strip().split('.')[1:]
            bot.send_message(chat_id, ''.join(info))
        bot.send_message(chat_id, f"Больше информации по ссылке {response_page.url}")
    except:
        bot.send_message(message.chat.id, 'Во Вселенной Гарри Поттера нет такого существа или волшебника.'
                                          ' Возможно, Вы допустили ошибку в слове :(')


def get_info(page):
    for description in page.find('div', id='mw-content-text').findChildren('p', recursive=False):
        return description.text


# писать повторяющийся код при вызове функции и передавать объект супа
def get_photo(page):
    photo = page.find('a', class_="image image-thumbnail").get('href')
    return photo


# creates connection to MySQL
def create_connection(host_name, user_name, password, db):
    connection = None
    try:
        connection = mysql.connector.connect(
            host = host_name,
            user = user_name,
            passwd = password,
            database = db
        )
        # print('Connection to MySQL DB is successful')
    except Error as e:
        pass
        # print(f" The error'{e}'occurred")
    return connection


def create_db(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        # print('DB created successfully')
    except Error as e:
        pass
        # print(f"The error '{e}' occurred")


# makes any query
def make_query(connection, query, name, data=''):
    cursor = connection.cursor()
    try:
        cursor.execute(query, data) if data != '' else cursor.execute(query)
        connection.commit()
        # print(f"The query '{name}' has occurred successfully")
    except Error as e:
        pass
        # print(f"The error '{e}' has occurred")


bot.polling(none_stop=True)  # Long Polling. none_stop=True - bot trying not to stop because of any errors
