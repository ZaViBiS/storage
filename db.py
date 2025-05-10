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

    def get_last(self):
        with self.Session() as session:
            return session.query(SensorsData).order_by(SensorsData.id.desc()).first()

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

    def get_for(self, for_time: int | float, time_gap: int):
        """for_time - проміжок часу в unix за який треба дані
        time_gap - проміжок між даними в хвилинах"""
        now = datetime.datetime.now().timestamp()

        with self.Session() as session:
            data = (
                session.query(SensorsData)
                .filter(SensorsData.time > now - for_time)
                .all()
            )

        res = []
        for x in range(0, len(data) - time_gap + 1, time_gap):
            group = data[x : x + time_gap]
            res.append(
                {
                    "time": round(sum([x.time for x in group]) / time_gap, 2),
                    "temp": round(sum([x.temp for x in group]) / time_gap, 2),
                    "hum": round(sum([x.hum for x in group]) / time_gap, 2),
                    "fan_speed": round(sum([x.fan_speed for x in group]) / time_gap, 2),
                    "vpd": round(sum([x.vpd for x in group]) / time_gap, 2),
                }
            )
        return res
