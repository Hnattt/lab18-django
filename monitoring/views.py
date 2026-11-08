from django.db.models import Avg,Count
from django.shortcuts import get_object_or_404,render
from django.views.decorators.http import require_safe
from .models import Device
@require_safe
def index(request):
 q=request.GET.get('q','').strip(); devices=Device.objects.annotate(n=Count('measurements'),mean=Avg('measurements__temperature')).order_by('serial')
 if q: devices=devices.filter(name__icontains=q)
 return render(request,'monitoring/index.html',{'devices':devices,'q':q})
@require_safe
def device_detail(request,pk):
 device=get_object_or_404(Device,pk=pk)
 return render(request,'monitoring/detail.html',{'device':device,'measurements':device.measurements.order_by('-measured_at','-pk')})

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from .forms import MeasurementForm
@login_required
@require_http_methods(['GET','POST'])
def measurement_create(request):
 form=MeasurementForm(request.POST if request.method=='POST' else None,user=request.user)
 if request.method=='POST' and form.is_valid():
  measurement=form.save()
  return redirect('monitoring:detail',pk=measurement.device_id)
 return render(request,'monitoring/measurement_form.html',{'form':form})
