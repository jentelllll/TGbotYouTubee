import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from pytube import YouTube, Channel
from config import TOKEN
from aiogram.dispatcher import FSMContext

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

if not os.path.exists("video"):
    os.makedirs("video")
if not os.path.exists("audio"):
    os.makedirs("audio")


@dp.message_handler(content_types=types.ContentTypes.STICKER)
async def sticker_message(message: types.Message):
    await message.answer("Будь ласка, відправте посилання, а не стікер.")


@dp.message_handler(content_types=types.ContentTypes.VIDEO)
async def video_message(message: types.Message):
    await message.answer("Будь ласка, відправте посилання, а не відео.")


@dp.message_handler(content_types=types.ContentTypes.PHOTO)
async def photo_message(message: types.Message):
    await message.answer("Будь ласка, відправте посилання, а не фото.")


@dp.message_handler(content_types=types.ContentTypes.VOICE)
async def voice_message(message: types.Message):
    await message.answer("Будь ласка, відправте посилання, а не голосове повідомлення.")



@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    buttons1 = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Почнемо😎", callback_data="start_button")]
        ]
    )
    await bot.send_message(message.chat.id, "Привіт!!👌\nЦей бот допоможе тобі скачувати\nвідео з платформи YouTube😉",
                           reply_markup=buttons1)


@dp.callback_query_handler(text="start_button")
async def process_start_button(callback_query: types.CallbackQuery):
    await callback_query.answer()
    await callback_query.message.edit_text(
        "Виберіть, яке відео ви хочете скачати відправте мені посилання, та натисніть : \nЗавантажити відео🎥 \n              або \nЗавантажити аудіо🎙")


def delete_files_in_directory(directory_path):
    try:
        files = os.listdir(directory_path)
        for file in files:
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print("All files deleted successfully.")
    except OSError:
        print("Error occurred while deleting files.")

def send_video_preview(link):
    yt = YouTube(link)
    channel = Channel(yt.channel_url)
    preview_url = yt.thumbnail_url
    publish_date = yt.publish_date if yt.publish_date else "Невідома дата"
    caption_text = f"""Прев'ю відео:
👉Назва: {yt.title}
👉Автор : {channel.channel_name}
👉Дата публікації : {publish_date}
👉Тривалість: {yt.length} секунд
👉Кількість переглядів : {yt.views}"""
    return preview_url, caption_text

def download_and_send_audio(link):
    yt = YouTube(link)
    audio = yt.streams.filter(only_audio=True).first()
    destination = "audio"
    out_file = audio.download(output_path=destination)
    base, ext = os.path.splitext(out_file)
    new_file = base + ".mp3"
    os.rename(out_file, new_file)


def download_and_send_video(link):
    yt = YouTube(link)
    yt_stream = yt.streams.get_highest_resolution()
    yt_stream.download(output_path="video")
    print("Завантаження завершено успішно")


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def text_message(message: types.Message, state: FSMContext):
    buttons2 = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Завантажити відео🎥", callback_data="download_video")],
            [types.InlineKeyboardButton(text="Завантажити аудіо🎙", callback_data="download_audio")]
        ]
    )
    link = message.text
    if "https://" in link:
        async with state.proxy() as data:
            data["link"] = link
        link_result = send_video_preview(link)
        preview_url, caption_text = send_video_preview(link)
        chat_id = message.chat.id
        if link_result:
            await bot.send_photo(chat_id=chat_id, photo=preview_url, caption=caption_text, reply_markup=buttons2)
    else:
        await message.answer("Будь ласка, введіть правильне посилання на відео з YouTube.")


@dp.callback_query_handler(text="download_audio")
async def audio_download_callback(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        link = data["link"]
    download_and_send_audio(link)
    await bot.send_audio(chat_id=call.from_user.id, audio=open("audio/" + os.listdir("audio")[0], "rb"))
    delete_files_in_directory("audio")


@dp.callback_query_handler(text="download_video")
async def video_download_callback(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        link = data["link"]
    download_and_send_video(link)
    await bot.send_video(chat_id=call.from_user.id, video=open("video/" + os.listdir("video")[0], "rb"))
    delete_files_in_directory("video")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
