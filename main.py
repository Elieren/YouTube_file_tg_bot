import os
import requests
import telebot
from pytubefix import YouTube
import io
from dotenv.main import load_dotenv
import datetime
from pydub import AudioSegment
import asyncio
from telebot.async_telebot import AsyncTeleBot

load_dotenv()
token = os.environ['TOKEN']


async def log(text):
    with open("log", "a") as f:
        f.write(str(datetime.datetime.now()) + "\t\t" + text + " " + "\n")


async def preview(message, url):
    await bot.send_message(message.chat.id, 'Пожалуйста подождите...')

    try:
        url_im = f'https://i.ytimg.com/vi/{url}/maxresdefault.jpg'
        r = requests.get(url_im)
        data = r.content
        await log(f"Preview download --> {message.chat.id} {url}")

        try:
            await bot.send_photo(message.chat.id, data)
            await log(f"Preview sent --> {message.chat.id} {url}")
        except Exception as e:
            await log(f"Error send preview --> {message.chat.id} {url} {e}")
            await bot.send_message(
                message.chat.id,
                'Error: Данное превью неполучается отправить')
    except Exception as e:
        await log(f"Error download preview --> {message.chat.id} {url} {e}")
        await bot.send_message(message.chat.id,
                               'Error: Данное превью нельзя скачать')


async def video(message, url):
    """Скачивание видео и отправка пользователю"""
    await bot.send_message(message.chat.id, 'Пожалуйста подождите...')

    # Загружаем видео с YouTube
    url = f'https://www.youtube.com/watch?v={url}'
    yt = YouTube(url)
    video_buffer = io.BytesIO()
    try:
        stream = yt.streams.get_highest_resolution()
        await log(f"Video download --> {message.chat.id} {url}")
        file_size = yt.streams.get_highest_resolution().filesize
        file_size_mb = file_size / (1024*1024)
        if file_size_mb <= 50.0:
            try:
                stream.stream_to_buffer(video_buffer)
                video_data = video_buffer.getbuffer()

                # Отправляем файл пользователю
                try:
                    await bot.send_video(message.chat.id,
                                         video_data, supports_streaming=True)
                except Exception as e:
                    await bot.send_message(message.chat.id, e)

                await log(f"Video sent --> {message.chat.id} {url}")

            except Exception as e:
                await log(f"Error send video --> {message.chat.id} {url} {e}")
                await bot.send_message(message.chat.id,
                                       'Error: Данное видео нельзя отправить')
        else:
            await bot.send_message(
                message.chat.id,
                'Это видео слишком большое для отправки.')
            download_url = yt.streams.get_highest_resolution().url
            await bot.send_message(
                message.chat.id,
                f'Ссылка для скачивания видео {download_url}')

    except Exception as e:
        await log(f"Error download video --> {message.chat.id} {url} {e}")
        await bot.send_message(message.chat.id,
                               'Error: Данное видео нельзя скачать')


async def audio(message, url):
    """Скачивание аудио и отправка пользователю"""
    await bot.send_message(message.chat.id, 'Пожалуйста подождите...')

    # Загружаем аудио с YouTube
    url = f'https://www.youtube.com/watch?v={url}'
    yt = YouTube(url)
    video_id = yt.video_id
    title = yt.title
    author = yt.author
    try:
        url_im = f'https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg'
        r = requests.get(url_im)
        data = r.content
        await log(f"Audio preview download --> {message.chat.id} {url}")

        try:
            audio_buffer = io.BytesIO()
            stream = yt.streams.get_audio_only()

            try:
                stream.stream_to_buffer(audio_buffer)
                audio_data = audio_buffer.getvalue()

                sound = AudioSegment.from_file(io.BytesIO(audio_data),
                                               format="mp4")
                audio_convert = io.BytesIO()
                sound.export(audio_convert, format="mp3")
                audio_convert = audio_convert.getvalue()
                audio_buffer.close()

                size = (len(audio_convert) / (1024 * 1024))

                if size <= 50.0:
                    # Отправляем файл пользователю
                    try:
                        await bot.send_audio(message.chat.id,
                                             audio=audio_convert,
                                             title=title, thumb=data,
                                             performer=author)
                    except Exception as e:
                        await bot.send_message(message.chat.id, e)

                    await log(f"Audio sent --> {message.chat.id} {url}")
                else:
                    await bot.send_message(
                        message.chat.id,
                        'Данное аудио слишком большое для отправки.')

            except Exception as e:
                await log(
                    f"Error send audio --> {message.chat.id} {url} {e}")
                await bot.send_message(message.chat.id,
                                       'Error: Данное аудио нельзя отправить')

        except Exception as e:
            await log(f"Error download audio --> {message.chat.id} {url} {e}")
            await bot.send_message(message.chat.id,
                                   'Error: Данное аудио нельзя скачать')

    except Exception as e:
        await log(
            f"Error download preview audio --> {message.chat.id} {url} {e}")
        await bot.send_message(message.chat.id,
                               'Error: Данное аудио нельзя скачать')

bot = AsyncTeleBot(token)


@bot.message_handler(commands=["start"])
async def start(message, res=False):
    await bot.send_message(
        message.chat.id,
        'Здравствуйте.\nОтправьте мне ссылку \
и я пришлю вам видео, аудио или превью.')
    await log(f"Start --> {message.chat.id} authorized ")


@bot.message_handler(content_types=["text"])
async def handle_message(message):
    """Обрабатываем сообщения от пользователей"""
    try:
        print(f'New url received from user {message.chat.id} (authorized)')
        # Получаем ссылку из сообщения пользователя
        url = message.text.strip()
        yt = YouTube(url)
        url = yt.video_id
        await log(f"Text --> {message.chat.id} {url}")
        markup = telebot.types.InlineKeyboardMarkup()
        button1 = telebot.types.InlineKeyboardButton(
            "Видео", callback_data=f'Видео {url}')
        button2 = telebot.types.InlineKeyboardButton(
            "Аудио", callback_data=f'Аудио {url}')
        button3 = telebot.types.InlineKeyboardButton(
            "Превью", callback_data=f'Превью {url}')
        # Добавляем кнопки в объект markup
        markup.add(button1, button2, button3)
        await bot.send_message(message.chat.id,
                               "Что скачать:", reply_markup=markup)

    except Exception as e:
        """Отправляем сообщение об ошибке пользователю"""
        await bot.send_message(message.chat.id, "Ошибка: " + str(e))
        await log(f"Error --> {str(e)}")


@bot.callback_query_handler(func=lambda call: True)
async def answer(call):
    """Обработка нажатия кнопки и запуск соответствующей функции"""
    result = call.data.split()
    if result[0] == 'Видео':
        await video(call.message, result[1])
    elif result[0] == 'Аудио':
        await audio(call.message, result[1])
    elif result[0] == 'Превью':
        await preview(call.message, result[1])


# Запускаем телеграм-бота
print('SERVER START')
asyncio.run(bot.polling(none_stop=True))
