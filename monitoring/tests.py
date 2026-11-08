from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError,transaction
from .models import Device
class DeviceTests(TestCase):
 def setUp(self):
  self.a=Device.objects.create(name='Холод камера',serial='V03-A'); Device.objects.create(name='Холод шлюз',serial='V03-B'); Device.objects.create(name='Склад',serial='V03-C')
 def test_pages_search(self):
  self.assertEqual(self.client.get('/').status_code,200); self.assertEqual(self.client.get(f'/devices/{self.a.pk}/').status_code,200); self.assertEqual(self.client.get('/devices/999/').status_code,404); self.assertEqual(self.client.post('/').status_code,405)
  before=Device.objects.count(); r=self.client.get('/',{'q':'Холод'}); self.assertEqual(len(r.context['devices']),2); self.assertEqual(len(self.client.get('/',{'q':''}).context['devices']),3); self.assertEqual(len(self.client.get('/',{'q':'неіснуючий-зразок'}).context['devices']),0); self.assertEqual(Device.objects.count(),before)
 def test_empty(self):
  Device.objects.all().delete(); self.assertContains(self.client.get('/'),'Пристроїв немає')
 def test_duplicate(self):
  with self.assertRaises(IntegrityError), transaction.atomic(): Device.objects.create(name='Дубль',serial=self.a.serial)
 def test_admin_rights(self):
  u=get_user_model().objects.create_user(username='regular',password='local-test'); self.client.force_login(u); self.assertEqual(self.client.get('/admin/').status_code,302)
  admin=get_user_model().objects.create_superuser(username='admin',password='local-test'); self.client.force_login(admin)
  r=self.client.post('/admin/monitoring/device/add/',{'name':'Тестовий','serial':'ADMIN-DEMO'}); self.assertEqual(r.status_code,302); self.assertTrue(Device.objects.filter(serial='ADMIN-DEMO').exists())

from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db.models import Avg,Count
from django.db.models.deletion import ProtectedError
from django.utils import timezone
from .models import Measurement,Passport,Tag
class RelationsTests(TestCase):
 def test_integrity_and_queries(self):
  d=Device.objects.create(name='Холод камера',serial='C1'); empty=Device.objects.create(name='Склад',serial='C2'); tag=Tag.objects.create(name='Холод'); d.tags.add(tag); Passport.objects.create(device=empty,location='Склад')
  a=Measurement.objects.create(device=d,temperature=Decimal('-5.00'),measured_at=timezone.now()); Measurement.objects.create(device=d,temperature=Decimal('5.00'),measured_at=timezone.now())
  self.assertEqual(Measurement.objects.aggregate(mean=Avg('temperature'))['mean'],Decimal('0')); self.assertEqual(Measurement.objects.filter(temperature__gt=0).count(),1)
  self.assertEqual(Device.objects.filter(tags__name='Холод').distinct().count(),1); self.assertIsNone(Device.objects.annotate(mean=Avg('measurements__temperature')).get(pk=empty.pk).mean)
  a.temperature=Decimal('-4.00'); a.save(); a.refresh_from_db(); self.assertEqual(a.temperature,Decimal('-4.00')); a.delete(); self.assertEqual(d.measurements.count(),1)
  with self.assertRaises(ProtectedError): d.delete()
  self.assertEqual(d.measurements.count(),1); empty.delete(); self.assertFalse(Passport.objects.exists())
 def test_validation_and_db_constraint(self):
  d=Device.objects.create(name='Холод',serial='C1')
  for v in ('-80','150'): Measurement(device=d,temperature=Decimal(v)).full_clean()
  with self.assertRaises(ValidationError): Measurement(device=d,temperature=Decimal('151')).full_clean()
  with self.assertRaises(IntegrityError),transaction.atomic(): Measurement.objects.create(device=d,temperature=Decimal('151'))

from datetime import timedelta
from django.test import Client,SimpleTestCase
class MeanExample(SimpleTestCase):
 def test_expected_mean(self): self.assertEqual((Decimal('20.00')+Decimal('30.00'))/2,Decimal('25.00'))
class FormSecurityTests(TestCase):
 def setUp(self):
  U=get_user_model(); self.a=U.objects.create_user(username='a',password='local-test'); self.b=U.objects.create_user(username='b',password='local-test',is_staff=True)
  self.own=Device.objects.create(name='Холод камера',serial='D1',owner=self.a); self.other=Device.objects.create(name='Холод шлюз',serial='D2',owner=self.b); self.unowned=Device.objects.create(name='Склад',serial='D3')
  self.date=(timezone.now()-timedelta(days=1)).isoformat(); self.url='/measurements/new/'
 def payload(self,device=None,temp='0',when=None): return {'device':(device or self.own).pk,'temperature':temp,'measured_at':when or self.date}
 def test_own_and_foreign_two_users(self):
  self.client.force_login(self.a); r=self.client.post(self.url,self.payload()); self.assertEqual(r.status_code,302); self.assertEqual(Measurement.objects.count(),1); self.assertEqual(self.own.measurements.count(),1)
  self.client.force_login(self.b); r=self.client.post(self.url,self.payload()); self.assertEqual(r.status_code,200); self.assertIn('device',r.context['form'].errors); self.assertEqual(Measurement.objects.count(),1); self.assertEqual(self.own.measurements.count(),1)
 def test_unowned_unknown_and_empty(self):
  self.client.force_login(self.a)
  for p in [self.payload(self.unowned),{'device':99999,'temperature':'0','measured_at':self.date},{}]:
   r=self.client.post(self.url,p); self.assertEqual(r.status_code,200); self.assertTrue(r.context['form'].is_bound); self.assertTrue(r.context['form'].errors); self.assertEqual(Measurement.objects.count(),0)
  self.assertIn('device',self.client.post(self.url,self.payload(self.unowned)).context['form'].errors)
  self.assertIn('device',self.client.post(self.url,{'device':99999,'temperature':'0','measured_at':self.date}).context['form'].errors)
  empty=self.client.post(self.url,{})
  self.assertTrue(empty.context['form'].is_bound)
  self.assertEqual(set(empty.context['form'].errors),{'device','temperature','measured_at'})
  self.assertEqual(Measurement.objects.count(),0)
 def test_get_choices_put_and_anonymous(self):
  self.assertEqual(self.client.get(self.url).status_code,302); self.client.force_login(self.a); r=self.client.get(self.url); self.assertEqual(list(r.context['form'].fields['device'].queryset),[self.own]); self.assertEqual(Measurement.objects.count(),0); self.assertEqual(self.client.put(self.url).status_code,405)
 def test_csrf_independent(self):
  c=Client(enforce_csrf_checks=True); c.force_login(self.a); self.assertEqual(c.post(self.url,self.payload()).status_code,403)
  self.assertEqual(Measurement.objects.count(),0)
  c.get(self.url); token=c.cookies['csrftoken'].value
  self.assertEqual(c.post(self.url,{**self.payload(),'csrfmiddlewaretoken':token}).status_code,302); self.assertEqual(Measurement.objects.count(),1)
  r=c.post(self.url,{**self.payload(self.other),'csrfmiddlewaretoken':token}); self.assertEqual(r.status_code,200); self.assertIn('device',r.context['form'].errors); self.assertEqual(Measurement.objects.count(),1)
 def test_temperature_boundaries(self):
  self.client.force_login(self.a)
  for value in ('-80','150'): self.assertEqual(self.client.post(self.url,self.payload(temp=value)).status_code,302)
  self.assertEqual(Measurement.objects.count(),2); r=self.client.post(self.url,self.payload(temp='151')); self.assertEqual(r.status_code,200); self.assertIn('temperature',r.context['form'].errors); self.assertEqual(Measurement.objects.count(),2)
 def test_detail_sorted_aware(self):
  now=timezone.now(); Measurement.objects.create(device=self.own,temperature=0,measured_at=now-timedelta(hours=1)); newest=Measurement.objects.create(device=self.own,temperature=1,measured_at=now)
  r=self.client.get(f'/devices/{self.own.pk}/'); self.assertEqual(list(r.context['measurements'])[0],newest); self.assertTrue(timezone.is_aware(newest.measured_at))
 def test_owner_protected(self):
  with self.assertRaises(ProtectedError): self.a.delete()
  self.assertTrue(Device.objects.filter(pk=self.own.pk).exists())

from datetime import datetime, timezone as dt_timezone
class ProfileVariant3Tests(TestCase):
 def setUp(self):
  self.a=Device.objects.create(name='Холод камера',serial='V03-A')
  self.b=Device.objects.create(name='Холод шлюз',serial='V03-B')
  self.c=Device.objects.create(name='Склад',serial='V03-C')
  for d,values in [(self.a,['-8.00','-6.00','-7.00','1.00','-5.00']),(self.b,['-3.00','-4.00','-1.00','2.00','-2.00'])]:
   for i,value in enumerate(values):
    Measurement.objects.create(device=d,temperature=Decimal(value),measured_at=datetime(2026,10,3,8+i//2,(i%2)*30,tzinfo=dt_timezone.utc))
  Passport.objects.create(device=self.a,location='Камера зразків'); Passport.objects.create(device=self.b,location='Шлюз зразків')
  cool=Tag.objects.create(name='Охолодження'); sample=Tag.objects.create(name='Зразки'); reserve=Tag.objects.create(name='Резерв')
  self.a.tags.add(cool,sample); self.b.tags.add(cool); self.c.tags.add(reserve)
 def test_profile_aggregates_and_search(self):
  rows={d.serial:d for d in Device.objects.annotate(n=Count('measurements'),mean=Avg('measurements__temperature'))}
  self.assertEqual(rows['V03-A'].n,5); self.assertEqual(rows['V03-A'].mean,Decimal('-5'))
  self.assertEqual(rows['V03-B'].n,5); self.assertEqual(rows['V03-B'].mean,Decimal('-1.6'))
  self.assertEqual(rows['V03-C'].n,0); self.assertIsNone(rows['V03-C'].mean)
  self.assertEqual(Measurement.objects.filter(temperature__gt=0).count(),2)
  self.assertEqual(set(Device.objects.filter(tags__name='Охолодження').values_list('serial',flat=True)),{'V03-A','V03-B'})
  response=self.client.get('/',{'q':'Холод'}); self.assertEqual(set(d.serial for d in response.context['devices']),{'V03-A','V03-B'})
 def test_below_zero_is_marked(self):
  d=Device.objects.create(name='Контроль',serial='boundary-test')
  neg=Measurement.objects.create(device=d,temperature=Decimal('-0.01'))
  r=self.client.get(f'/devices/{d.pk}/'); self.assertContains(r,f'data-measurement-id="{neg.pk}" data-below="true"'); self.assertContains(r,'Нижче 0 °C',count=1)
 def test_zero_and_positive_are_not_marked(self):
  d=Device.objects.create(name='Контроль',serial='boundary-test')
  zero=Measurement.objects.create(device=d,temperature=Decimal('0.00')); pos=Measurement.objects.create(device=d,temperature=Decimal('0.01'))
  r=self.client.get(f'/devices/{d.pk}/')
  for m in (zero,pos): self.assertContains(r,f'data-measurement-id="{m.pk}" data-below="false"')
  self.assertNotContains(r,'Нижче 0 °C')
