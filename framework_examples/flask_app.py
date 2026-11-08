from flask import Flask, jsonify, render_template, abort
from .common import DEVICES,find_device
app=Flask(__name__)
@app.get('/')
def home(): return render_template('devices.html',devices=DEVICES)
@app.get('/devices')
def devices(): return jsonify(DEVICES)
@app.get('/devices/<int:device_id>')
def detail(device_id):
 d=find_device(device_id)
 if d is None: abort(404)
 return jsonify(d)
