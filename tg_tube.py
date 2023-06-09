import os
import requests
import shutil
import telebot
from pytube import YouTube
import os
import time
import sys
import io
from dotenv.main import load_dotenv
import datetime
from pydub import AudioSegment
from pydub.utils import mediainfo
import asyncio
import aiohttp
from telebot.async_telebot import AsyncTeleBot

load_dotenv()
token = os.environ['TOKEN']
id_telegram = os.environ['ID_TELEGRAM']

id_telegram = id_telegram.split(', ')

async def log(text):
    with open("log", "a") as f:
        f.write(str(datetime.datetime.now())+ "\t\t" + text + " " +"\n")

async def video(message, url):
    """Скачивание видео и отправка пользователю"""
    await bot.send_message(message.chat.id, 'Пожалуйста подождите...')
    
    # Загружаем видео с YouTube
    yt = YouTube(url)
    video_buffer = io.BytesIO()
    stream = yt.streams.get_highest_resolution()
    try:
        stream.stream_to_buffer(video_buffer)
        video_data = video_buffer.getbuffer()

        # Отправляем файл пользователю
        while True:
            try:
                await bot.send_video(message.chat.id, video_data, supports_streaming=True)
                break
            except:
                pass
            
        await log(f"Video sent --> {message.chat.id} {url}")
    except:
        await log(f"Error download video --> {message.chat.id} {url}")
        await bot.send_message(message.chat.id, 'Error: Данное видео нельзя скачать')
        
async def audio(message, url):
    """Скачивание аудио и отправка пользователю"""
    await bot.send_message(message.chat.id, 'Пожалуйста подождите...')

    # Загружаем аудио с YouTube
    yt = YouTube(url)
    video_id = yt.video_id
    title = yt.title
    url_im = f'https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg'
    r = requests.get(url_im)
    data = r.content

    audio_buffer = io.BytesIO()
    stream = yt.streams.get_audio_only()
    try:
        stream.stream_to_buffer(audio_buffer)
        audio_data = audio_buffer.getvalue()

        sound = AudioSegment.from_file(io.BytesIO(audio_data), format="mp4")
        audio_convert = io.BytesIO()
        sound.export(audio_convert, format="mp3")
        audio_convert = audio_convert.getvalue()
        audio_buffer.close()
        # Отправляем файл пользователю
        while True:
            try:
                await bot.send_audio(message.chat.id, audio=audio_convert, title=title, thumb=data)
                break
            except:
                pass

        await log(f"Audio sent --> {message.chat.id} {url}")
    except:
        await log(f"Error download audio --> {message.chat.id} {url}")
        await bot.send_message(message.chat.id, 'Error: Данное аудио нельзя скачать')

bot = AsyncTeleBot(token)

async def notuser(message, status):
    """Отправка сообщения о запрете"""
    await bot.send_message(message.chat.id, 'Здравствуйте.\nИспользование бота для вашего профиля запрещено.')
    await log(f"{status} --> {message.chat.id} not authorized ")

@bot.message_handler(commands=["start"])
async def start(message, res=False):
    if str(message.chat.id) in id_telegram:
        await bot.send_message(message.chat.id, 'Здравствуйте.\nОтправьте мне ссылку и я пришлю вам видео или аудио файл.')
        await log(f"Start --> {message.chat.id} authorized ")
    else:
        await notuser(message, "Start")
    print(f'New message received from user {message.chat.id}')

@bot.message_handler(content_types=["text"])
async def handle_message(message):
    """Обрабатываем сообщения от пользователей"""
    try:
        if str(message.chat.id) in id_telegram:
            print(f'New url received from user {message.chat.id} (authorized)')
            url = message.text.strip() # Получаем ссылку из сообщения пользователя
            log(f"Text --> {message.chat.id} {url}")
            markup = telebot.types.InlineKeyboardMarkup()
            button1 = telebot.types.InlineKeyboardButton("Видео", callback_data=f'Видео {url}')
            button2 = telebot.types.InlineKeyboardButton("Аудио", callback_data=f'Аудио {url}')
            markup.add(button1, button2)  # Добавляем кнопки в объект markup
            await bot.send_message(message.chat.id, "Что скачать:", reply_markup=markup)
        else:
            print(f'New url received from user {message.chat.id} (not authorized)')
            await notuser(message, "Text")
    
    except Exception as e:
        """Отправляем сообщение об ошибке пользователю"""
        await bot.send_message(message.chat.id, "Ошибка: " + str(e))
        await log(f"Error --> {str(e)}")
    

@bot.callback_query_handler(func = lambda call: True)
async def answer(call):
    """Обработка нажатия кнопки и запуск соответствующей функции"""
    result = call.data.split()
    if result[0] == 'Видео':
        await video(call.message, result[1])
    elif result[0] == 'Аудио':
        await audio(call.message, result[1])


# Запускаем телеграм-бота
print('SERVER START')
asyncio.run(bot.polling(none_stop=True))
