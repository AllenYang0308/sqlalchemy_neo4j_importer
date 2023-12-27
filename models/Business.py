from sqlalchemy import (
    String, Integer,
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


class Business(Base):

    __tablename__ = "business"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    business_id: Mapped[str] = mapped_column(String(80))
    business_name: Mapped[str] = mapped_column(String(80))
    business_address: Mapped[str] = mapped_column(String(80))
    city: Mapped[str] = mapped_column(String(80))
    bzip: Mapped[str] = mapped_column(String(80))
    latitude: Mapped[str] = mapped_column(String(80))
    longitude: Mapped[str] = mapped_column(String(80))
    user_name: Mapped[str] = mapped_column(String(80))
    deviceID: Mapped[str] = mapped_column(String(80))
    scan_timestamp: Mapped[str] = mapped_column(String(80))
