from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import HTTPException


class Repository:
    model = None

    def __init__(self, session: Session):
        self.session = session

    def list(self):
        return self.session.scalars(
            select(self.model).order_by(self.model.created_at)
        ).all()

    def get(self, record_id: str):
        record = self.session.get(self.model, record_id)
        if record is None:
            raise HTTPException(404, f"{self.model.__name__} not found")
        return record

    def create(self, values):
        record = self.model(**values)
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

    def update(self, record, values):
        for key, value in values.items():
            setattr(record, key, value)
        record.version += 1
        self.session.commit()
        self.session.refresh(record)
        return record

    def delete(self, record):
        self.session.delete(record)
        self.session.commit()
