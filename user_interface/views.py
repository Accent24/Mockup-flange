from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.shortcuts import render, redirect, HttpResponse, reverse
from lib.SAPyLib import connect_to_sa
from .models import MainFunction, FillForm, ProjectTolerance
from .sa_functions import *
from django.core import serializers
import json


# Start SA Sdk and connect
def start_sdk(request):
    sa_sdk = check_for_sa_instance()

    if sa_sdk[0]:
        return redirect('home')
    else:
        return render(request, 'user_interface/sa_failed.html', {'message': sa_sdk[1]})


# API to test active connection with SDK
def test_sdk(request):
    connection = connect_to_sa()
    return HttpResponse(connection[0])


class HomePage(ListView):
    template_name = 'user_interface/home.html'
    model = MainFunction


class FillFormCreate(CreateView):
    model = FillForm
    template_name = 'user_interface/form.html'
    fields = ['employee_id',
              'employee_name',
              'job_number',
              'wo_number',
              'steel_temperature',
              'fabrication_stage']


    def form_valid(self, form):
        form.instance.station_name = MainFunction.objects.get(pk=self.kwargs['pk'])

        return super().form_valid(form)


class FillFormUpdate(UpdateView):
    model = FillForm
    template_name = 'user_interface/form.html'
    fields = ['employee_id',
              'employee_name',
              'job_number',
              'wo_number',
              'steel_temperature',
              'fabrication_stage']


def plate_inspection(request, pk):
    # sa_plate_inspection()

    form_object = FillForm.objects.get(pk=pk)

    form_dic = serializers.serialize('json', [form_object])
    tolerance_dic = serializers.serialize('json',
                                      ProjectTolerance.objects.filter(station_name_id=form_object.station_name.pk))

    return render(request, template_name='user_interface/inspection/plate_inspection.html',
                  context={'form_pk': pk})


def sys_exit(request):
    close_app()

    return HttpResponse('')

class CanInspection(TemplateView):
    ...


class FlangeInspection(TemplateView):
    ...

