from typing import Any, Dict, List, Optional, Union
from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, field_validator, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Настройки приложения
    """
    PROJECT_NAME: str = "Parking App"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS настройки
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode='before')
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # JWT настройки
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # База данных
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @model_validator(mode='after')
    def assemble_db_connection(self) -> 'Settings':
        if values := self.dict():
            if not self.SQLALCHEMY_DATABASE_URI:
                self.SQLALCHEMY_DATABASE_URI = PostgresDsn.build(
                    scheme="postgresql+asyncpg",
                    username=values.get("POSTGRES_USER"),
                    password=values.get("POSTGRES_PASSWORD"),
                    host=values.get("POSTGRES_SERVER"),
                    path=f"/{values.get('POSTGRES_DB') or ''}"
                )
        return self

    # Redis
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # Celery
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Почта
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    # Парковка
    BOOKING_MAX_DURATION: int = 24  # часов
    BOOKING_RESERVATION_DURATION: int = 15  # минут
    NOTIFICATION_TIMES: List[int] = [60, 15, 5]  # минут до окончания

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()