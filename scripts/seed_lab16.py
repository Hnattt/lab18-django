from pathlib import Path
import json
from django.db import transaction
from monitoring.models import Device
p=next(x for x in json.loads(Path("profiles_15_18.json").read_text(encoding="utf-8")) if x["variant"]==3)
with transaction.atomic():
    if Device.objects.exists(): raise RuntimeError("Потрібна порожня навчальна база")
    for item in p["devices"]: Device.objects.create(**item)
print("Створено пристрої профілю",[(d["name"],d["serial"]) for d in p["devices"]])
