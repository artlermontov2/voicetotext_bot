import os
from dotenv import load_dotenv
import speech_recognition as sr
from pydub import AudioSegment
import telebot


load_dotenv()

BOT_TOKEN = os.getenv("TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет, перешли мне аудиосообщение")

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    # Скачать голосовое сообщение
    file_info = bot.get_file(message.voice.file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # Сохранить голосовое сообщение в формате .ogg
    with open("voice.ogg", 'wb') as new_file:
        new_file.write(downloaded_file)

    # Конвертировать .ogg в .wav для распознавания
    audio = AudioSegment.from_ogg("voice.ogg")
    audio.export("voice.wav", format="wav")

    # Использовать SpeechRecognition для перевода в текст
    recognizer = sr.Recognizer()
    with sr.AudioFile("voice.wav") as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language='ru-RU')
            bot.reply_to(message, text)
        except sr.UnknownValueError:
            bot.reply_to(message, "Извините, я не смог распознать текст.")
        except sr.RequestError:
            bot.reply_to(message, "Ошибка сервиса распознавания.")

    # Удаление временных файлов
    os.remove("voice.ogg")
    os.remove("voice.wav")


bot.infinity_polling()