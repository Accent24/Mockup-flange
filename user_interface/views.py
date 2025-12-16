from django.template.context_processors import request
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.shortcuts import render, redirect, HttpResponse, reverse
import json
import string
from lib.SAPyLib import connect_to_sa
from .models import MainFunction, FillForm, ProjectNominalAndTolerance
from .sa_functions import *
from django.core import serializers
import win32gui
import pywintypes
from win32con import HWND_TOP
import time

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


# API to test if instrument is currently connected to SA
def test_instrument(request):
    return HttpResponse(check_for_instrument_connection())


def stop_instrument_interface(request):
    return HttpResponse(sa.stop_instrument_interface(collection_inst='Inspection', id_inst=0))


def load_and_start(request, template_name):
    message = open_template_check_connection(template_name)

    return HttpResponse(message)


def measure(request, collection, group, name, target_type):
    message = measure_pt(collection, group, name, target_type)

    return HttpResponse(message)


def spatial_scan(request, collection, group):
    cancel_measurement_and_start_new(collection, group, 'Plate scan')

    return HttpResponse()


def ovc(request):
    message = sa.instrument_operational_check(collection_inst='Inspection', id_inst=0, check_type='Camera View')

    while True:
        window_handle = win32gui.FindWindow(None, 'Overview Camera')

        if win32gui.IsWindow(window_handle):
            win32gui.SetWindowPos(window_handle, HWND_TOP, 1000, 100, 900, 800, 0)
            break
        time.sleep(1.0)

    return HttpResponse(message)


def ovc_close(request):
    message = sa.instrument_operational_check(collection_inst='Inspection', id_inst=0, check_type='Close Camera View')

    return HttpResponse(message)


def rough_alignment(request):
    message = sa.run_subroutine('template::rough alignment.mp', False, True)

    return HttpResponse(message)


def automatic_alignment(request):
    message = sa.run_subroutine('template::automatic alignment.mp', False, True)

    return HttpResponse(message)

# automatic inspection and analysis. returns results
def inspection(request, num_dim):
    char_list = string.ascii_lowercase
    expected_return_dic = dict()

    for char_index in range(0, num_dim):
        expected_return_dic[char_list[char_index]] = 'float'

    result = sa.run_subroutine('Template::inspection.mp', False, True, expected_return_dic)

    return HttpResponse(json.dumps({'result': result[0], 'dimensions': result[1]}))


def clear_measurement(request):
    message = sa.run_subroutine('template::clear.mp', False, True)

    return HttpResponse(message)


class HomePage(ListView):
    template_name = 'user_interface/home.html'
    model = MainFunction


class FillFormCreate(CreateView):
    model = FillForm
    template_name = 'user_interface/form.html'
    fields = ['operator',
              'tp_number',
              'can_ref',
              'steel_temperature',
              'fabrication_stage']


    def form_valid(self, form):
        form.instance.station_name = MainFunction.objects.get(pk=self.kwargs['pk'])

        return super().form_valid(form)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['station_name'] = MainFunction.objects.get(pk=self.kwargs['pk']).name
        return context


class FillFormUpdate(UpdateView):
    model = FillForm
    template_name = 'user_interface/form.html'
    fields = ['operator',
              'tp_number',
              'can_ref',
              'steel_temperature',
              'fabrication_stage']


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['station_name'] = FillForm.objects.get(pk=self.kwargs['pk']).station_name
        return context


def plate_inspection(request, pk):
    # sa_plate_inspection()

    form_object = FillForm.objects.get(pk=pk)

    form_dic = serializers.serialize('json', [form_object])
    tolerance_dic = serializers.serialize('json',
                                      ProjectNominalAndTolerance.objects.filter(station_name_id=form_object.station_name.pk))

    fill_form_query = FillForm.objects.get(pk=pk)
    query_set = ProjectNominalAndTolerance.objects.filter(station_name=fill_form_query.station_name.pk,
                                                          can_ref=fill_form_query.can_ref)

    return render(request, template_name='user_interface/inspection/plate_inspection.html',
                  context={'form_pk': pk,
                           'required_n_tolerance_list': query_set,
                           'num_dim': len(query_set)})


def flange_inspection(request, pk):
    station_id = FillForm.objects.get(pk=pk).station_name.pk
    query_set = ProjectNominalAndTolerance.objects.filter(station_name=station_id)

    return render(request, template_name='user_interface/inspection/flange_inspection.html',
                  context={'form_pk': pk,
                           'required_n_tolerance_list': query_set,
                           'num_dim': len(query_set)})


def bring_window_foreground(request):
    def enum_handler(hwnd, lParam):
        if ' - Google Chrome' in win32gui.GetWindowText(hwnd):
            try:
                win32gui.SetForegroundWindow(hwnd)
            except pywintypes.error:
                pass

    if not win32gui.FindWindow(None, 'Overview Camera'):
        win32gui.EnumWindows(enum_handler, None)

    return  HttpResponse()


def generate_report(request, form_pk):
    sa.run_subroutine("Template::report.mp", True, True)

    query_object = FillForm.objects.get(pk=form_pk)

    report_number = 'CN/24/2106/HAM/GL/PL/TP{0}/{1}/DC002'.format(query_object.tp_number, query_object.can_ref)
    report_tags = {'Tp': str(query_object.tp_number),
                   'Can': query_object.can_ref,
                   'Operator': query_object.operator.full_name,
                   'Temperature': str(query_object.steel_temperature),
                   'Report number': report_number}

    for k, v in report_tags.items():
        sa.set_report_value_from_string(k, v)

    sa.output_SA_report_to_PDF('Report', 'Report',
                               '../Reports/{0}.pdf'.format(report_number.replace('/', '_')), True)

    return HttpResponse()


def sys_exit(request):
    close_app()

    return HttpResponse('')

class CanInspection(TemplateView):
    ...


class FlangeInspection(TemplateView):
    ...


def test(request):

    return HttpResponse()

