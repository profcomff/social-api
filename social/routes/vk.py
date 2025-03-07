import logging

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, BackgroundTasks, Depends, Request
from fastapi.responses import PlainTextResponse
from fastapi_sqlalchemy import db
from pydantic import BaseModel, ConfigDict

from social.handlers_vk.base import process_event
from social.models.group import VkGroup
from social.models.webhook_storage import WebhookStorage, WebhookSystems
from social.settings import get_settings
from social.utils.string import random_string
from social.utils.vk_groups import create_vk_chat


router = APIRouter(prefix="/vk", tags=['vk'])
settings = get_settings()
logger = logging.getLogger(__name__)


class VkGroupCreate(BaseModel):
    confirmation_token: str
    change_secret_key: bool = False


class VkGroupCreateResponse(BaseModel):
    group_id: int
    secret_key: str

    model_config = ConfigDict(from_attributes=True)


class MonitoringConfig(BaseModel):
    vk_group_id: int
    telegram_channel_id: int


@router.post('', tags=["webhooks"])
async def vk_webhook(request: Request, background_tasks: BackgroundTasks) -> str:
    """Принимает любой POST запрос от VK"""
    try:
        request_data = await request.json()
        logger.debug(f"Received VK webhook: {request_data}")
        group_id = request_data.get("group_id")  # Получаем ID группы
        
        if not group_id:
            logger.warning("Received VK webhook without group_id")
            return PlainTextResponse('ok')  # Возвращаем ok, чтобы VK не пытался повторить запрос
        
        # Проверяем наличие группы в базе данных
        group = db.session.query(VkGroup).where(VkGroup.group_id == group_id).one_or_none()
        
        if not group:
            logger.warning(f"Received VK webhook for unknown group_id: {group_id}")
            return PlainTextResponse('ok')
        
        # Проверка на создание нового вебхука со страницы ВК
        if request_data.get("type", "") == "confirmation":
            logger.info(f"Received confirmation request for group_id: {group_id}")
            return PlainTextResponse(group.confirmation_token)
        
        # Проверка секретного ключа
        if request_data.get("secret") != group.secret_key:
            logger.warning(f"Received VK webhook with invalid secret for group_id: {group_id}")
            return PlainTextResponse('ok')  # Возвращаем ok, но не обрабатываем
        
        event_type = request_data.get("type", "unknown")
        logger.info(f"Processing VK webhook, type: {event_type}, group_id: {group_id}")
        
        # Сохраняем событие в базу данных
        db.session.add(
            WebhookStorage(
                system=WebhookSystems.VK,
                message=request_data,
            )
        )
        db.session.commit()
        
        # Проверяем, это ли событие создания записи на стене
        is_wall_post = event_type == "wall_post_new"
        if is_wall_post:
            logger.info(f"Received new wall post event for group_id: {group_id}")
        
        # Запускаем обработку в фоновом режиме
        background_tasks.add_task(create_vk_chat, request_data)
        background_tasks.add_task(process_event, request_data)
        
        return PlainTextResponse('ok')
    except Exception as e:
        logger.exception(f"Error processing VK webhook: {e}")
        return PlainTextResponse('ok')  # Всегда возвращаем ok, чтобы VK не повторял запрос


@router.put('/{group_id}')
def create_or_replace_group(
    group_id: int,
    group_info: VkGroupCreate,
    user: dict[str] = Depends(UnionAuth(["social.group.create"])),
) -> VkGroupCreateResponse:
    group = db.session.query(VkGroup).where(VkGroup.group_id == group_id).one_or_none()
    if group is None:
        group = VkGroup()
        group.owner_id = user.get("id")
        db.session.add(group)
        group.group_id = group_id
        group.secret_key = random_string(32)

    if group_info.change_secret_key:
        group.secret_key = random_string(32)

    group.confirmation_token = group_info.confirmation_token

    db.session.commit()
    return group


@router.post('/monitoring/configure')
def configure_monitoring(
    config: MonitoringConfig,
    user: dict[str] = Depends(UnionAuth(["social.monitoring.configure"])),
) -> dict:
    """Настраивает мониторинг группы ВК и пересылку постов в Telegram канал"""
    # Здесь мы обновляем настройки приложения
    # В реальном приложении нужно будет сохранять эти настройки в базу данных
    # и загружать их при старте, а не менять глобальный объект
    
    settings = get_settings()
    
    # В данном примере мы напрямую изменяем настройки
    # Но лучше будет сохранить их в базу и обновлять при перезапуске
    # Для этого потребуется создать соответствующую модель БД
    settings.VK_MONITORED_GROUP_ID = config.vk_group_id
    settings.TELEGRAM_TARGET_CHANNEL_ID = config.telegram_channel_id
    
    logger.info(f"Monitoring configured for VK group {config.vk_group_id} with Telegram channel {config.telegram_channel_id}")
    
    return {
        "status": "success",
        "message": "Мониторинг настроен успешно",
        "vk_group_id": config.vk_group_id,
        "telegram_channel_id": config.telegram_channel_id
    }
