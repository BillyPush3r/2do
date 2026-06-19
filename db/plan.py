from uuid import uuid4
from datetime import datetime, timezone
from db.models import Plan
from sqlmodel import Session, select
from db.engine import get_engine


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_new_plan(title: str | None = None) -> Plan | None:
    engine = get_engine()
    with Session(engine) as session:
        title = title if title else datetime.now().isoformat()[:19]
        existing = session.exec(select(Plan).where(Plan.title == title)).first()
        if existing:
            return None
        now = _now()
        plan = Plan(
            uuid=str(uuid4()),
            title=title,
            tasks=[],
            created_at=now,
            updated_at=now,
        )
        session.add(plan)
        session.commit()
        session.refresh(plan)
        return plan


def get_plans() -> list[Plan]:
    engine = get_engine()
    with Session(engine) as session:
        statement = select(Plan)
        return list(session.exec(statement).all())


def get_plan(identifier: str) -> Plan | None:
    engine = get_engine()
    with Session(engine) as session:
        statement = select(Plan).where(Plan.uuid == identifier)
        plan = session.exec(statement).first()
        if plan:
            return plan
        statement = select(Plan).where(Plan.title == identifier)
        return session.exec(statement).first()


def delete_plan(identifier: str) -> bool:
    engine = get_engine()
    with Session(engine) as session:
        plan = get_plan(identifier)
        if plan:
            session.delete(plan)
            session.commit()
            return True
        return False


def rename_plan(identifier: str, new_title: str) -> bool:
    engine = get_engine()
    with Session(engine) as session:
        plan = get_plan(identifier)
        if not plan:
            return False
        existing = session.exec(select(Plan).where(Plan.title == new_title)).first()
        if existing:
            return False
        plan.title = new_title
        plan.updated_at = _now()
        session.add(plan)
        session.commit()
        session.refresh(plan)
        return True
