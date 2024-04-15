class SocialApiError(Exception):
    """Корневая ошибка Social API"""


class GroupRequestNotFound(SocialApiError):
    """Не найдено запроса на создание группы"""

    def __init__(self, user_id: int, secret_key: str, *args) -> None:
        self.user_id = user_id
        self.secret_key = secret_key
        super().__init__(*args)
