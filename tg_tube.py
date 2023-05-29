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

try:
    load_dotenv()
    token = os.environ['TOKEN']
    id_telegram = os.environ['ID_TELEGRAM']
    
    id_telegram = id_telegram.split(', ')

    def video(message, url):
        """Скачивание видео и отправка пользователю"""
        bot.send_message(message.chat.id, 'Пожалуйста подождите...')
        while True:
            try:
                # Загружаем видео с YouTube
                yt = YouTube(url)
                video_buffer = io.BytesIO()
                stream = yt.streams.get_highest_resolution()
                stream.stream_to_buffer(video_buffer)
                video_data = video_buffer.getbuffer()
                video_buffer.flush()

                # Отправляем файл пользователю
                while True:
                    try:
                        bot.send_video(message.chat.id, video_data, supports_streaming=True)
                        break
                    except:
                        pass
                break

            except:
                pass
            
    def audio(message, url):
        """Скачивание аудио и отправка пользователю"""
        bot.send_message(message.chat.id, 'Пожалуйста подождите...')
        while True:
            try:
                # Загружаем аудио с YouTube
                yt = YouTube(url)
                audio_buffer = io.BytesIO()
                stream = yt.streams.get_audio_only()
                stream.stream_to_buffer(audio_buffer)
                audio_data = audio_buffer.getbuffer()
                audio_buffer.flush()
                
                # Отправляем файл пользователю
                while True:
                    try:
                        bot.send_audio(message.chat.id, audio_data)
                        break
                    except:
                        pass
                break
            
            except:
                pass

    bot = telebot.TeleBot(token)

    def notuser(message):
        """Отправка сообщения о запрете"""
        bot.send_message(message.chat.id, 'Здравствуйте.\nИспользование бота для вашего профиля запрещено.')

    @bot.message_handler(commands=["start"])
    def start(message, res=False):
        if str(message.chat.id) in id_telegram:
            bot.send_message(message.chat.id, 'Здравствуйте.\nОтправьте мне ссылку и я пришлю вам видео или аудио файл.')
        else:
            notuser(message)
        print(f'New message received from user {message.chat.id}')

    @bot.message_handler(content_types=["text"])
    def handle_message(message):
        """Обрабатываем сообщения от пользователей"""
        try:
            if str(message.chat.id) in id_telegram:
                print(f'New url received from user {message.chat.id} (authorized)')
                url = message.text.strip() # Получаем ссылку из сообщения пользователя
                markup = telebot.types.InlineKeyboardMarkup()
                button1 = telebot.types.InlineKeyboardButton("Видео", callback_data=f'Видео {url}')
                button2 = telebot.types.InlineKeyboardButton("Аудио", callback_data=f'Аудио {url}')
                markup.add(button1, button2)  # Добавляем кнопки в объект markup
                bot.send_message(message.chat.id, "Что скачать:", reply_markup=markup)
            else:
                print(f'New url received from user {message.chat.id} (not authorized)')
                notuser(message)
        
        except Exception as e:
            """Отправляем сообщение об ошибке пользователю"""
            bot.send_message(message.chat.id, "Ошибка: " + str(e))
        

    @bot.callback_query_handler(func = lambda call: True)
    def answer(call):
        """Обработка нажатия кнопки и запуск соответствующей функции"""
        if call.data[:5] == 'Видео':
            video(call.message, call.data[6:])
        elif call.data[:5] == 'Аудио':
            audio(call.message, call.data[6:])

    # Запускаем телеграм-бота
    print('SERVER START')
    bot.polling(none_stop=True)

except:
    # При ошибку полностью перезапускаем программу
    print("SERVER ERROR --- SERVER RESTART")
    os.execv(sys.executable, ['python3'] + sys.argv)
