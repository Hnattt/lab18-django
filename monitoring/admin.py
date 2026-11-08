from django.contrib import admin
from .models import Device, Tag, Passport, Measurement
@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
 list_display=['name','serial']
 search_fields=['name','serial']
admin.site.register(Tag); admin.site.register(Passport); admin.site.register(Measurement)
