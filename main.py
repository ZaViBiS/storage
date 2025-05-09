import fastapi
import datetime
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db import DataBase


class Data(BaseModel):
    time: int
    fan_speed: int
    hum: float
    temp: float
    vpd: float


app = fastapi.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://zavibis.github.io", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DataBase()


@app.post("/put")
def get_data(data: Data):
    db.put(data.time, data.fan_speed, data.hum, data.temp, data.vpd)


@app.get("/all")
def get_all():
    return db.get_all()


@app.get("/hour")
def give_hour():
    return db.get_for(datetime.timedelta(hours=1).total_seconds(), 1)


@app.get("/day")
def give_day():
    return db.get_for(datetime.timedelta(days=1).total_seconds(), 5)


@app.get("/week")
def give_week():
    return db.get_for(datetime.timedelta(weeks=1).total_seconds(), 20)


@app.get("/month")
def give_month():
    return db.get_for(datetime.timedelta(days=30).total_seconds(), 60)
