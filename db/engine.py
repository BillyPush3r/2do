import os
from sqlmodel import SQLModel, create_engine, Session, text
from db.models import Plan, Task, CommandHistory  # noqa: F401

from dotenv import load_dotenv

load_dotenv()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'database.db')
engine = create_engine(f'sqlite:///{DB_PATH}', echo=False)


def get_engine():
    return engine


def _migrate():
    try:
        with Session(engine) as session:
            conn = session.connection()
            for col, col_type in [('allocated_minutes', 'INTEGER'), ('pomodoro_count', 'INTEGER DEFAULT 0')]:
                try:
                    conn.execute(text(f'ALTER TABLE task ADD COLUMN {col} {col_type}'))
                except Exception:
                    pass
            session.commit()
    except Exception:
        pass


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    _migrate()
