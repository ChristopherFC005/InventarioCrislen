import os
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()


class Base(DeclarativeBase):
    pass


def _connection_url() -> str:
    server = os.getenv("DB_SERVER", r"localhost\SQLEXPRESS")
    database = os.getenv("DB_NAME", "CrislenInventario")
    driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
    auth_mode = os.getenv("DB_AUTH_MODE", "windows").lower()
    options = f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};TrustServerCertificate=yes;"
    if auth_mode == "windows":
        options += "Trusted_Connection=yes;"
    else:
        options += f"UID={os.getenv('DB_USER', '')};PWD={os.getenv('DB_PASSWORD', '')};"
    return f"mssql+pyodbc:///?odbc_connect={quote_plus(options)}"


engine = create_engine(_connection_url(), pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_database() -> None:
    from app import models  # registra los modelos antes de crear tablas
    Base.metadata.create_all(engine)
