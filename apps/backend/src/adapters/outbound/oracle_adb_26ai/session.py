import os

from config.settings import settings
from sqlmodel import Session, create_engine

os.environ.setdefault("TNS_ADMIN", settings.tns_admin)

engine = create_engine(
    f"oracle+oracledb://{settings.db_user}:{settings.db_password}@{settings.db_dsn}",
    echo=True,
)


def get_session():
    with Session(engine) as session:
        yield session
