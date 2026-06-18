import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

password = os.getenv("DB_PASSWORD")

database_url = (
    f"postgresql+psycopg://postgres:{password}"
    f"@localhost:5432/freelance_monitor"
    )

engine = create_engine(database_url, echo=False)
SessionLocal = sessionmaker(bind=engine)
