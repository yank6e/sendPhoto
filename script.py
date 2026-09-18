import os
import random
import time
import cv2
from loader import bot
from pyrogram.types import InputMediaPhoto, InputMediaVideo
from pathlib import Path
import mimetypes

#folder = 'photos' #datetime.fromtimestamp(os.path.getmtime(file_path))

def main(folder):

    extension = ('.jpg', '.jpeg', '.png', '.webp', '.mp4', '.mov', '.avi', '.mkv')
    image_extension = ('.jpg', '.jpeg', '.png', '.webp')
    video_extension = ('.mp4', '.mov', '.avi', '.mkv')
    photos_paths = []

    exist = False
    if os.path.exists(folder) and os.path.isdir(folder):
        exist = True

    try:
        for image in os.listdir(folder):

            if image.endswith(extension):
                photos_paths.append(os.path.join(folder, image))
                print("Совпало")
            else:
                print("Не то")
    except:
        print("Ошибка")
        return

    sorted_photos_paths = sorted(photos_paths)
    #print(sorted_photos_paths)

    # группируем по 10 фотографий
    chunks = [sorted_photos_paths[i : i + 10] for i in range(0, len(sorted_photos_paths), 10)]

    with bot:
        for chunk in chunks:
            media_group = []
            for b in chunk:
                mime_type, _= mimetypes.guess_type(b)

                if mime_type:
                    if mime_type.startswith('image/'):
                        print("Это фото")
                        media_group.append(InputMediaPhoto(media=b))
                    elif mime_type.startswith('video/'):
                        print("Это видео")
                        media_group.append(InputMediaVideo(media=b))
                    else:
                        print("Не понятно че это")

            if media_group:
                bot.send_media_group(chat_id='me', media=media_group)

if __name__ == "__main__":
    while True:
        folder_path = input("Введите путь: ")
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            print("Папка есть")
            main(folder_path)
            break
        else:
            print("Введите правильно")
