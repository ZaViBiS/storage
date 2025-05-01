import fastapi
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
    allow_origins=["https://zavibis.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DataBase()


@app.post("/put")
def get_data(data: Data):
    db.put(data.time, data.fan_speed, data.hum, data.temp, data.vpd)


@app.get("/")
def give():
    return db.get_for_last_24h()
