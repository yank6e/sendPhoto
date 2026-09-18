import os
import random
import time
import cv2
from loader import bot
from pyrogram.types import InputMediaPhoto, InputMediaVideo

PHOTOS_DIR = "photos"


def generate_video_thumbnail(video_path, thumb_path):
  """Автоматически извлекает первый кадр из видео и сохраняет как превью (JPEG)"""
  try:
    cap = cv2.VideoCapture(video_path)
    success, frame = cap.read()
    if success:
      # Изменяем размер, если кадр слишком большой (Telegram требует до 320px)
      h, w = frame.shape[:2]
      max_size = 320
      if max(h, w) > max_size:
        scale = max_size / max(h, w)
        frame = cv2.resize(
            frame, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA
        )

      cv2.imwrite(thumb_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
      cap.release()
      return True
    cap.release()
  except Exception as e:
    print(f"⚠️ Не удалось сгенерировать превью для {video_path}: {e}")
  return False


def main():
  if not os.path.exists(PHOTOS_DIR):
    print(f"Папка '{PHOTOS_DIR}' не найдена в текущей директории.")
    return

  photo_extensions = (".jpg", ".jpeg", ".png", ".webp")
  video_extensions = (".mp4", ".mov", ".avi", ".mkv")

  files = sorted(os.listdir(PHOTOS_DIR))
  media_files = []

  for file in files:
    file_lower = file.lower()
    full_path = os.path.join(PHOTOS_DIR, file)

    if file_lower.endswith(photo_extensions):
      media_files.append(("photo", full_path))
    elif file_lower.endswith(video_extensions):
      base_name = os.path.splitext(full_path)[0]
      thumb_path = base_name + "_thumb.jpg"

      # Ищем ручную обложку или генерируем автоматически
      if not os.path.exists(thumb_path):
        # Проверяем, может есть файл с тем же именем но расширением картинки
        for ext in photo_extensions:
          if os.path.exists(base_name + ext):
            thumb_path = base_name + ext
            break
        else:
          # Если ручной обложки нет — генерируем через OpenCV
          success = generate_video_thumbnail(full_path, thumb_path)
          if not success:
            thumb_path = None

      media_files.append(("video", full_path, thumb_path))

  if not media_files:
    print(f"В папке '{PHOTOS_DIR}' не найдено подходящих медиафайлов.")
    return

  print(
      f"Всего найдено файлов: {len(media_files)}. Начинаем отправку в"
      " Избранное..."
  )

  chunks = [
      media_files[i : i + 10] for i in range(0, len(media_files), 10)
  ]

  with bot:
    for group_idx, chunk in enumerate(chunks, start=1):
      media_group = []

      for item in chunk:
        if item[0] == "photo":
          media_group.append(InputMediaPhoto(media=item[1]))
        elif item[0] == "video":
          video_path, thumb_path = item[1], item[2]
          media_group.append(
              InputMediaVideo(
                  media=video_path,
                  thumb=thumb_path if thumb_path and os.path.exists(thumb_path) else None,
                  supports_streaming=True,
              )
          )

      try:
        bot.send_media_group(chat_id="me", media=media_group)
        print(f"✅ Отправлена группа #{group_idx} (файлов: {len(media_group)})")
      except Exception as e:
        print(f"❌ Ошибка при отправке группы #{group_idx}: {e}")

      if group_idx < len(chunks):
        delay = random.uniform(3.0, 7.0)
        print(f"⏳ Пауза {delay:.1f} сек...")
        time.sleep(delay)

  print("🎉 Все файлы успешно отправлены!")


if __name__ == "__main__":
  main()
