import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Integer, Float
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

Base = declarative_base()


class SensorsData(Base):
    __tablename__ = "sensors"
    time: Mapped[int] = mapped_column(Integer, nullable=False)
    fan_speed: Mapped[int] = mapped_column(Integer, nullable=False)
    hum: Mapped[float] = mapped_column(Float, nullable=False)
    temp: Mapped[float] = mapped_column(Float, nullable=False)
    vpd: Mapped[float] = mapped_column(Float, nullable=False)
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


DATABASE_URL = "sqlite:///data.sqlite3"

engine = create_engine(DATABASE_URL)


Base.metadata.create_all(engine)  # Створює таблиці, якщо їх немає


class DataBase:
    def __init__(self) -> None:
        self.Session = sessionmaker(bind=engine)

    def put(
        self, time: int, fan_speed: int, hum: float, temp: float, vpd: float
    ) -> None:
        data = SensorsData(time=time, fan_speed=fan_speed, hum=hum, temp=temp, vpd=vpd)
        with self.Session.begin() as session:
            session.add(data)

    def get_all(self):
        with self.Session() as session:
            for data in session.query(SensorsData).all():
                yield data

    def get_for_last_24h(self):
        now = datetime.datetime.now().timestamp()
        with self.Session() as session:
            return (
                session.query(SensorsData)
                .filter(SensorsData.time > now - (24 * 60 * 60))
                .all()
            )
