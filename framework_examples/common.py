"""Незалежні вигадані дані для порівняння фреймворків."""
DEVICES=[{'id':1,'name':'Холод камера','serial':'DEMO-03-01'}, {'id':2,'name':'Холод шлюз','serial':'DEMO-03-02'}]
def find_device(device_id):
 return next((d.copy() for d in DEVICES if d['id']==device_id),None)
