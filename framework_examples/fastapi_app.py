from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .common import DEVICES,find_device
class DeviceResponse(BaseModel):
 id: int
 name: str
 serial: str
app=FastAPI()
@app.get('/devices',response_model=list[DeviceResponse])
def devices(): return DEVICES
@app.get('/devices/{device_id}',response_model=DeviceResponse)
def detail(device_id: int):
 d=find_device(device_id)
 if d is None: raise HTTPException(status_code=404,detail='Пристрій не знайдено')
 return d
