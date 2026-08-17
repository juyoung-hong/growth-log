from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    db_user: str
    db_password: str
    db_dsn: str
    tns_admin: str

    oci_config_profile: str = "DEFAULT"  # OCI config에 존재하는 프로필 이름
    oci_bucket_name: str
    oci_autonomous_database_id: (
        str  # ADB OCID — 콘솔의 Autonomous Database 상세 페이지에서 복사
    )

    upload_max_bytes: int = 20 * 1024 * 1024  # 20MB
    image_resize_max_px: int = 2000
    image_jpeg_quality: int = 85

    db_capacity_bytes: int = 20 * 1024**3  # OCI Always Free ADB 한도 20GB
    object_storage_capacity_bytes: int = (
        10 * 1024**3
    )  # OCI Always Free Object Storage 한도 10GB
    storage_warning_threshold: float = 0.8  # 80% 이상이면 경고


settings = Settings()
