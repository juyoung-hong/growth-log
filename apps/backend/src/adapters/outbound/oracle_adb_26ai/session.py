import os

from sqlalchemy import event
from sqlmodel import Session, create_engine

from config.settings import settings

os.environ.setdefault("TNS_ADMIN", settings.tns_admin)

engine = create_engine(
    f"oracle+oracledb://{settings.db_user}:{settings.db_password}@{settings.db_dsn}",
    echo=True,
)


def get_session():
    with Session(engine) as session:
        yield session


@event.listens_for(engine, "connect")
def _set_char_semantics(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("ALTER SESSION SET NLS_LENGTH_SEMANTICS = CHAR")
    cursor.close()
