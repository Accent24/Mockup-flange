import json

from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.shortcuts import render, redirect, HttpResponse, reverse
from pyexpat.errors import messages

from lib.SAPyLib import connect_to_sa
from .models import MainFunction, FillForm, ProjectTolerance
from .sa_functions import *
from django.core import serializers


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


def load_and_start(request, template_name):
    message = open_template_check_connection(template_name)

    return HttpResponse(message)

def measure(request, collection, group, name, target_type):
    message = measure_pt(collection, group, name, target_type)

    return HttpResponse(message)


def ovc(request):
    message = sa.instrument_operational_check(collection_inst='', id_inst=0, check_type='Camera View')

    return HttpResponse(message)


def ovc_close(request):
    message = sa.instrument_operational_check(collection_inst='', id_inst=0, check_type='Close Camera View')

    return HttpResponse(message)


def rough_alignment(request):
    message = sa.run_subroutine('template::rough alignment.mp', False, True)

    return HttpResponse(message)


def automatic_alignment(request):
    message = sa.run_subroutine('template::automatic alignment.mp', False, True)

    return HttpResponse(message)


def inspection(request):
    message = sa.run_subroutine('template::inspection.mp', False, True)

    return HttpResponse(message)


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


def flange_inspection(request, pk):
    return render(request, template_name='user_interface/inspection/flange_inspection.html',
                  context={'form_pk': pk})


def sys_exit(request):
    close_app()

    return HttpResponse('')

class CanInspection(TemplateView):
    ...


class FlangeInspection(TemplateView):
    ...


def test(request):
    result = sa.run_subroutine('Template::test.mp', False, True, {'a': 'float',
                                                                                              'b': 'float',
                                                                                              'c': 'float',
                                                                                              'd': 'float',
                                                                                              'e': 'float'})

    return HttpResponse(json.dumps({'result': result[0], 'dimensions': result[1]}))
