from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    db_user: str
    db_password: str
    db_dsn: str
    tns_admin: str

    upload_max_bytes: int = 20 * 1024 * 1024  # 20MB
    image_resize_max_px: int = 2000
    image_jpeg_quality: int = 85


settings = Settings()
