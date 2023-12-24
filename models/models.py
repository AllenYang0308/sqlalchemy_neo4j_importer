import random
from datetime import date
from typing import Optional
from sqlalchemy import (
    String, Date, Integer, CHAR,
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


class User(Base):

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
    birthday: Mapped[date] = mapped_column(Date, nullable=True)
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    idcode: Mapped[str] = mapped_column(CHAR(4), nullable=False)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __repr__(self) -> str:
        return f"User(id={self.uid!r}, \
            name={self.name!r}, \
            fullname={self.fullname!r})"

    def _set_uid(self, *args, **kwargs) -> None:
        rndkey = str(random.randint(0, 1000))
        self.uid = rndkey + self.name

    def preinsert(self, *args, **kwargs) -> None:
        self._set_uid(*args, **kwargs)
        print("preinsert")

    def to_dict(self) -> dict:
        return [row.__dict__ for row in self]


# sess = CreateSession()
#
#
# @event.listens_for(User, 'before_commit')
# def user_before_commit(sess):
#
#     print("This is before commit message.")
