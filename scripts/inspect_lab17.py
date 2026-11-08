from django.db.models import Avg,Count
from monitoring.models import Device,Measurement
print('Пристрій V03-A:',Measurement.objects.filter(device__serial='V03-A').count())
print('Діапазон -4..1:',Measurement.objects.filter(temperature__gte=-4,temperature__lte=1).count())
print('Дата 2026-10-03:',Measurement.objects.filter(measured_at__date='2026-10-03').count())
print('Охолодження:',list(Device.objects.filter(tags__name='Охолодження').order_by('serial').values_list('serial',flat=True)))
print('> 0:',Measurement.objects.filter(temperature__gt=0).count())
for d in Device.objects.annotate(n=Count('measurements'),mean=Avg('measurements__temperature')).order_by('serial'): print(d.serial,d.n,d.mean)
