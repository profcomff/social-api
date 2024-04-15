class SocialApiError(Exception):
    """Корневая ошибка Social API"""


class GroupRequestNotFound(SocialApiError):
    """Не найдено запроса на создание группы"""
