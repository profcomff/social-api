import logging
from collections.abc import Callable
import json
import re
import requests

from social.utils.events import EventProcessor
from social.utils.vk_groups import approve_vk_chat
from social.settings import get_settings
from telegram import Bot, InputMediaPhoto


logger = logging.getLogger(__name__)
EVENT_PROCESSORS: list[EventProcessor] = []
settings = get_settings()


def event(**filters: str):
    """Помечает функцию как обработчик событий, задает фильтры для запуска"""

    def deco(func: Callable):
        EVENT_PROCESSORS.append(EventProcessor(filters, func))
        return func

    return deco


def process_event(event: dict):
    for processor in EVENT_PROCESSORS:
        if processor.check_and_process(event):
            break
    else:
        logger.debug("Event without processor")


@event(
    type="message_new",
    object=lambda i: i.get("message", {}).get("text", "").startswith("/validate"),
)
def validate_group(event: dict):
    """Если получено сообщение команды /validate, то за группой закрепляется владелец"""
    approve_vk_chat(event)


async def send_to_telegram(message: str, photos: list = None):
    """Отправляет сообщение и фотографии в Telegram канал"""
    if not settings.TELEGRAM_BOT_TOKEN or not settings.TELEGRAM_TARGET_CHANNEL_ID:
        logger.warning("Telegram bot token or channel ID not configured")
        return

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    
    try:
        if not photos:
            # Если нет фотографий, отправляем только текст
            await bot.send_message(
                chat_id=settings.TELEGRAM_TARGET_CHANNEL_ID,
                text=message,
                parse_mode='HTML',
                disable_web_page_preview=False
            )
        elif len(photos) == 1:
            # Если только одна фотография, отправляем ее с подписью
            await bot.send_photo(
                chat_id=settings.TELEGRAM_TARGET_CHANNEL_ID,
                photo=photos[0],
                caption=message,
                parse_mode='HTML'
            )
        else:
            # Если несколько фотографий, отправляем их как медиагруппу
            media_group = []
            
            # Первая фотография с подписью (текстом сообщения)
            media_group.append(InputMediaPhoto(
                media=photos[0],
                caption=message,
                parse_mode='HTML'
            ))
            
            # Все остальные фотографии без подписи
            for photo_url in photos[1:]:
                media_group.append(InputMediaPhoto(
                    media=photo_url
                ))
            
            await bot.send_media_group(
                chat_id=settings.TELEGRAM_TARGET_CHANNEL_ID,
                media=media_group
            )
        
        logger.info(f"Message successfully sent to Telegram channel {settings.TELEGRAM_TARGET_CHANNEL_ID}")
    except Exception as e:
        logger.error(f"Failed to send message to Telegram: {e}")


@event(
    type="wall_post_new",
    group_id=lambda i: int(i) == settings.VK_MONITORED_GROUP_ID if settings.VK_MONITORED_GROUP_ID else False,
)
def handle_new_post(event: dict):
    """Обрабатывает событие нового поста в группе ВК и пересылает его в Telegram канал"""
    logger.info("New post detected in monitored VK group")
    
    try:
        # Получаем данные поста
        post = event.get("object", {})
        post_id = post.get("id")
        owner_id = post.get("owner_id")
        text = post.get("text", "")
        attachments = post.get("attachments", [])
        
        # Форматируем сообщение для Telegram
        message = f"<b>Новый пост в группе ВК:</b>\n\n{text}"
        
        # Добавляем информацию о вложениях, кроме фото (их отправим отдельно)
        attachment_texts = []
        
        for attachment in attachments:
            attachment_type = attachment.get("type")
            
            # Обрабатываем видео
            if attachment_type == "video":
                video_data = attachment.get("video", {})
                video_id = video_data.get("id")
                video_owner_id = video_data.get("owner_id")
                video_title = video_data.get("title", "Видео")
                
                if video_id and video_owner_id:
                    attachment_texts.append(
                        f"\n\n<b>📹 {video_title}</b>: "
                        f"<a href='https://vk.com/video{video_owner_id}_{video_id}'>Смотреть видео</a>"
                    )
            
            # Обрабатываем ссылки
            elif attachment_type == "link":
                link_data = attachment.get("link", {})
                link_url = link_data.get("url")
                link_title = link_data.get("title", "Ссылка")
                
                if link_url:
                    attachment_texts.append(
                        f"\n\n<b>🔗 {link_title}</b>: <a href='{link_url}'>Открыть ссылку</a>"
                    )
            
            # Обрабатываем документы
            elif attachment_type == "doc":
                doc_data = attachment.get("doc", {})
                doc_url = doc_data.get("url")
                doc_title = doc_data.get("title", "Документ")
                
                if doc_url:
                    attachment_texts.append(
                        f"\n\n<b>📄 {doc_title}</b>: <a href='{doc_url}'>Скачать документ</a>"
                    )
            
            # Обрабатываем аудио
            elif attachment_type == "audio":
                audio_data = attachment.get("audio", {})
                audio_id = audio_data.get("id")
                audio_owner_id = audio_data.get("owner_id")
                audio_artist = audio_data.get("artist", "")
                audio_title = audio_data.get("title", "Аудиозапись")
                
                if audio_id and audio_owner_id:
                    attachment_texts.append(
                        f"\n\n<b>🎵 {audio_artist} - {audio_title}</b>: "
                        f"<a href='https://vk.com/audio{audio_owner_id}_{audio_id}'>Слушать</a>"
                    )
        
        # Добавляем информацию о вложениях к сообщению
        if attachment_texts:
            message += "".join(attachment_texts)
        
        # Добавляем ссылку на оригинальный пост в конце
        message += f"\n\n<a href='https://vk.com/wall{owner_id}_{post_id}'>Оригинальный пост ВКонтакте</a>"
        
        # Собираем фотографии из вложений
        photos = []
        for attachment in attachments:
            if attachment.get("type") == "photo":
                photo_data = attachment.get("photo", {})
                # Выбираем максимальное разрешение фото
                sizes = photo_data.get("sizes", [])
                if sizes:
                    # Сортируем по размеру (width * height)
                    sizes.sort(key=lambda x: x.get("width", 0) * x.get("height", 0), reverse=True)
                    photo_url = sizes[0].get("url")
                    if photo_url:
                        photos.append(photo_url)
        
        # Отправляем в Telegram
        import asyncio
        asyncio.run(send_to_telegram(message, photos))
        
        logger.info(f"Post content forwarded to Telegram channel from VK post {owner_id}_{post_id}")
    except Exception as e:
        logger.exception(f"Error processing new VK post: {e}")
