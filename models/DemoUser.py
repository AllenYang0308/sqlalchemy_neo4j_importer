from typing import Optional
from sqlalchemy import (
    String, Integer, CHAR,
    create_engine
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
)

from sqlalchemy.orm import Session


def CreateSession():
    engine = create_engine(
        "mysql+pymysql://root:12345@localhost:3306/demo?charset=utf8mb4"
    )
    return Session(engine)


class Base(DeclarativeBase):

    def preinsert(self, *args, **kwargs):
        print("start")

    def soSomethingToField(self, field, func, **kwargs):
        print("soSomethingToField")


class DemoUser(Base):

    __tablename__ = "user_account"

    uid: Mapped[str] = mapped_column(
        String(50),
        primary_key=True
    )
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True
    )
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    idcode: Mapped[str] = mapped_column(CHAR(4), nullable=False)
