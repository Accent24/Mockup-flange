from django.views.generic import TemplateView, ListView, CreateView
from django.shortcuts import render, redirect, HttpResponse, reverse
from lib.SAPyLib import connect_to_sa
from .models import MainFunction, FillForm
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


class HomePage(ListView):
    template_name = 'user_interface/home.html'
    model = MainFunction


class FillFormView(CreateView):
    model = FillForm
    template_name = 'user_interface/form.html'
    fields = ['employee_id',
              'employee_name',
              'job_number',
              'wo_number',
              'steel_temperature',
              'fabrication_stage']


    def form_valid(self, form):
        form.instance.station_name = self.kwargs['station']

        return super().form_valid(form)


def plate_inspection(request, form_pk):
    # sa_plate_inspection()

    json_dic = serializers.serialize('json', [FillForm.objects.get(pk=form_pk)])

    return HttpResponse(json_dic)


def sys_exit(request):
    close_app()

    return HttpResponse('')

class CanInspection(TemplateView):
    ...


class FlangeInspection(TemplateView):
    ...

