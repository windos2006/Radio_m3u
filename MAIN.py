# Year: 2026
import telebot
import requests
import os
import configparser
import sys

def get_bot_token(config_path="config.ini"):
    """
    Парсит конфигурационный файл и возвращает токен бота.
    """
    if not os.path.exists(config_path):
        print(f"Критическая ошибка: Файл конфигурации '{config_path}' не найден.")
        print("Пожалуйста, создайте файл config.ini с секцией [Bot] и параметром Token.")
        sys.exit(1)

    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf-8')

    try:
        token = config.get("Bot", "Token")
        if not token or token == "ТВОЙ_ТОКЕН_ТЕЛЕГРАМ_БОТА":
            print("Критическая ошибка: Токен не задан. Замените значение по умолчанию в config.ini на ваш реальный токен.")
            sys.exit(1)
        return token
    except (configparser.NoSectionError, configparser.NoOptionError):
        print("Критическая ошибка: В файле конфигурации не найдена секция [Bot] или параметр Token.")
        sys.exit(1)

# Получаем токен из файла конфигурации
BOT_TOKEN = get_bot_token()
bot = telebot.TeleBot(BOT_TOKEN)

def search_radio_stations(query):
    """
    Выполняет поиск радиостанций в Radio Browser API.
    Ищет совпадения по названию, жанру (тегу) и стране.
    Возвращает список уникальных станций без ограничений по количеству.
    """
    base_url = "https://de1.api.radio-browser.info/json/stations/search"
    unique_stations = {}
    
    # 1. Поиск по названию
    try:
        req_name = requests.get(base_url, params={"name": query, "hidebroken": "true"})
        if req_name.status_code == 200:
            for station in req_name.json():
                unique_stations[station["stationuuid"]] = station
    except Exception as e:
        print(f"Ошибка при поиске по названию: {e}")

    # 2. Поиск по жанру (тегу)
    try:
        req_tag = requests.get(base_url, params={"tag": query, "hidebroken": "true"})
        if req_tag.status_code == 200:
            for station in req_tag.json():
                unique_stations[station["stationuuid"]] = station
    except Exception as e:
        print(f"Ошибка при поиске по жанру: {e}")

    # 3. Поиск по стране
    try:
        req_country = requests.get(base_url, params={"country": query, "hidebroken": "true"})
        if req_country.status_code == 200:
            for station in req_country.json():
                unique_stations[station["stationuuid"]] = station
    except Exception as e:
        print(f"Ошибка при поиске по стране: {e}")

    return list(unique_stations.values())

def create_m3u_content(stations):
    """
    Формирует текстовое содержимое для формата .m3u из списка станций.
    """
    lines = ["#EXTM3U"]
    for st in stations:
        name = st.get("name", "Неизвестная станция").replace("\n", " ").strip()
        url = st.get("url_resolved", st.get("url", ""))
        
        if url:
            lines.append(f"#EXTINF:-1,{name}")
            lines.append(url)
            
    return "\n".join(lines)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "Привет! Я бот для поиска интернет-радиостанций.\n\n"
        "Просто напиши мне любое слово: название станции, жанр (например, rock, jazz) "
        "или страну. Я соберу все доступные результаты и пришлю тебе готовый `.m3u` файл "
        "для твоего плеера."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(content_types=['text'])
def handle_search_request(message):
    query = message.text.strip()
    
    msg_in_progress = bot.reply_to(message, f"Начинаю поиск по запросу: «{query}»...\nПожалуйста, подожди, собираю все результаты.")
    
    stations = search_radio_stations(query)
    
    if not stations:
        bot.edit_message_text(
            chat_id=message.chat.id, 
            message_id=msg_in_progress.message_id, 
            text=f"К сожалению, по запросу «{query}» ничего не найдено."
        )
        return
    
    bot.edit_message_text(
        chat_id=message.chat.id, 
        message_id=msg_in_progress.message_id, 
        text=f"Найдено станций: {len(stations)}. Формирую и сохраняю файл..."
    )
    
    m3u_data = create_m3u_content(stations)
    
    safe_query = "".join(c if c.isalnum() else "_" for c in query)
    filename = f"playlist_{safe_query}.m3u"
    
    with open(filename, "w", encoding="utf-8") as file:
        file.write(m3u_data)
        
    with open(filename, "rb") as file:
        bot.send_document(
            message.chat.id, 
            file, 
            caption=f"Твой плейлист готов! В нем {len(stations)} станций."
        )
        
    try:
        os.remove(filename)
    except OSError as e:
        print(f"Не удалось удалить временный файл {filename}: {e}")

if __name__ == '__main__':
    print("Бот запущен и готов к работе...")
    bot.infinity_polling()
ции не найдена секция [Bot] или параметр Token.")
        sys.exit(1)

# Получаем токен из файла конфигурации
BOT_TOKEN = get_bot_token()
bot = telebot.TeleBot(BOT_TOKEN)

def search_radio_stations(query):
    """
    Выполняет поиск радиостанций в Radio Browser API.
    Ищет совпадения по названию, жанру (тегу) и стране.
    Возвращает список уникальных станций без ограничений по количеству.
    """
    base_url = "https://de1.api.radio-browser.info/json/stations/search"
    unique_stations = {}
    
    # 1. Поиск по названию
    try:
        req_name = requests.get(base_url, params={"name": query, "hidebroken": "true"})
        if req_name.status_code == 200:
            for station in req_name.json():
                unique_stations[station["stationuuid"]] = station
    except Exception as e:
        print(f"Ошибка при поиске по названию: {e}")

    # 2. Поиск по жанру (тегу)
    try:
        req_tag = requests.get(base_url, params={"tag": query, "hidebroken": "true"})
        if req_tag.status_code == 200:
            for station in req_tag.json():
                unique_stations[station["stationuuid"]] = station
    except Exception as e:
        print(f"Ошибка при поиске по жанру: {e}")

    # 3. Поиск по стране
    try:
        req_country = requests.get(base_url, params={"country": query, "hidebroken": "true"})
        if req_country.status_code == 200:
            for station in req_country.json():
                unique_stations[station["stationuuid"]] = station
    except Exception as e:
        print(f"Ошибка при поиске по стране: {e}")

    return list(unique_stations.values())

def create_m3u_content(stations):
    """
    Формирует текстовое содержимое для формата .m3u из списка станций.
    """
    lines = ["#EXTM3U"]
    for st in stations:
        name = st.get("name", "Неизвестная станция").replace("\n", " ").strip()
        url = st.get("url_resolved", st.get("url", ""))
        
        if url:
            lines.append(f"#EXTINF:-1,{name}")
            lines.append(url)
            
    return "\n".join(lines)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "Привет! Я бот для поиска интернет-радиостанций.\n\n"
        "Просто напиши мне любое слово: название станции, жанр (например, rock, jazz) "
        "или страну. Я соберу все доступные результаты и пришлю тебе готовый `.m3u` файл "
        "для твоего плеера."
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(content_types=['text'])
def handle_search_request(message):
    query = message.text.strip()
    
    msg_in_progress = bot.reply_to(message, f"Начинаю поиск по запросу: «{query}»...\nПожалуйста, подожди, собираю все результаты.")
    
    stations = search_radio_stations(query)
    
    if not stations:
        bot.edit_message_text(
            chat_id=message.chat.id, 
            message_id=msg_in_progress.message_id, 
            text=f"К сожалению, по запросу «{query}» ничего не найдено."
        )
        return
    
    bot.edit_message_text(
        chat_id=message.chat.id, 
        message_id=msg_in_progress.message_id, 
        text=f"Найдено станций: {len(stations)}. Формирую и сохраняю файл..."
    )
    
    m3u_data = create_m3u_content(stations)
    
    safe_query = "".join(c if c.isalnum() else "_" for c in query
