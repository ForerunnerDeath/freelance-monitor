from database import SessionLocal
import db_sqlalchemy


with SessionLocal() as session:
    print("unsent telegram:", db_sqlalchemy.get_unsent_telegram_count(session))