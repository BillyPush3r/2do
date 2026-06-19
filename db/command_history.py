from sqlmodel import Session, select
from db.models import CommandHistory
from db.engine import get_engine


def save_command(command: str):
    engine = get_engine()
    with Session(engine) as session:
        entry = CommandHistory(command=command)
        session.add(entry)
        session.commit()


def load_history(limit: int = 100) -> list[str]:
    engine = get_engine()
    with Session(engine) as session:
        statement = (
            select(CommandHistory.command)
            .order_by(CommandHistory.id.desc())
            .limit(limit)
        )
        results = session.exec(statement).all()
        return list(reversed(results))
