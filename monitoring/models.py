from decimal import Decimal
from django.core.validators import MinValueValidator,MaxValueValidator
from django.db import models
from django.conf import settings
from django.utils import timezone
class Tag(models.Model):
 name=models.CharField(max_length=80,unique=True)
 def __str__(self): return self.name
class Device(models.Model):
 owner=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='devices',null=True,blank=True)
 name=models.CharField(max_length=80)
 serial=models.CharField(max_length=40,unique=True)
 tags=models.ManyToManyField(Tag,blank=True,related_name='devices')
 def __str__(self): return f'{self.name} ({self.serial})'
class Passport(models.Model):
 device=models.OneToOneField(Device,on_delete=models.CASCADE,related_name='passport')
 location=models.CharField(max_length=120)
 def __str__(self): return f'{self.device.serial}: {self.location}'
class Measurement(models.Model):
 device=models.ForeignKey(Device,on_delete=models.PROTECT,related_name='measurements')
 temperature=models.DecimalField(max_digits=5,decimal_places=2,validators=[MinValueValidator(Decimal('-80')),MaxValueValidator(Decimal('150'))])
 measured_at=models.DateTimeField(default=timezone.now)
 class Meta:
  ordering=['-measured_at','-pk']
  constraints=[models.CheckConstraint(condition=models.Q(temperature__gte=-80,temperature__lte=150),name='temperature_range')]
 def __str__(self): return f'{self.device.serial}: {self.temperature} °C'
