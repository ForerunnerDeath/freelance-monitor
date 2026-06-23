import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

db_user = os.getenv("DB_USER", "postgres")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST", "localhost")
db_port = os.getenv("DB_PORT", "5432")
db_name = os.getenv("DB_NAME", "freelance_monitor")
db_connect_timeout = int(os.getenv("DB_CONNECT_TIMEOUT", "5"))

database_url = (
    f"postgresql+psycopg://{db_user}:{db_password}"
    f"@{db_host}:{db_port}/{db_name}"
    )

engine = create_engine(
    database_url,
    echo=False,
    connect_args={"connect_timeout": db_connect_timeout},
)
SessionLocal = sessionmaker(bind=engine)
