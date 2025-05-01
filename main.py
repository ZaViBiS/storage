import fastapi
from pydantic import BaseModel

from db import DataBase


class Data(BaseModel):
    time: int
    fan_speed: int
    hum: float
    temp: float
    vpd: float


app = fastapi.FastAPI()
db = DataBase()


@app.post("/put")
def get_data(data: Data):
    db.put(data.time, data.fan_speed, data.hum, data.temp, data.vpd)


@app.get("/")
def give():
    return db.get_for_last_24h()
