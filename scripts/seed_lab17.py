from pathlib import Path
import json
from decimal import Decimal
from datetime import datetime
from django.db import transaction
from django.db.models import Avg,Count
from monitoring.models import Device,Passport,Tag,Measurement
p=next(x for x in json.loads(Path("profiles_15_18.json").read_text(encoding="utf-8")) if x["variant"]==3)
with transaction.atomic():
    if Measurement.objects.exists() or Passport.objects.exists() or Tag.objects.exists(): raise RuntimeError("Дані вже існують; використайте нову базу")
    devices={d.serial:d for d in Device.objects.all()}
    if set(devices)!={x["serial"] for x in p["devices"]}: raise RuntimeError("Спочатку створіть саме три пристрої профілю")
    for item in p["passports"]: Passport.objects.create(device=devices[item["serial"]],location=item["location"])
    tags={name:Tag.objects.create(name=name) for name in p["tags"]}
    for serial,names in p["device_tags"].items(): devices[serial].tags.add(*(tags[name] for name in names))
    for m in p["measurements"]: Measurement.objects.create(device=devices[m["serial"]],temperature=Decimal(m["temperature"]),measured_at=datetime.fromisoformat(m["measured_at"]))
for d in Device.objects.annotate(n=Count("measurements"),mean=Avg("measurements__temperature")).order_by("serial"): print(d.serial,d.n,d.mean)
print("Строго вище 0:",Measurement.objects.filter(temperature__gt=Decimal(p["threshold"])).count())
print("Мітка Охолодження:",list(Device.objects.filter(tags__name="Охолодження").order_by("serial").values_list("serial",flat=True)))
