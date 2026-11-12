from django.db.models.fields import return_None
from django.template.context_processors import request
from django.views.generic import TemplateView, ListView, CreateView, UpdateView
from django.shortcuts import render, redirect, HttpResponse, reverse
import json
import string

from pymupdf import message

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


def start_instrument_interface(request):
    return HttpResponse(sa.start_instrument_interface(collection_inst='Inspection', id_inst=0, initialize=False))


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
            win32gui.SetWindowPos(window_handle, HWND_TOP, 1000, 100, 885, 800, 0)
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


def automatic_bcd(request):
    sa.run_subroutine('Template::auto bcd.mp', False, True)
    return HttpResponse()


def analysis(request, num_dim):
    char_list = string.ascii_lowercase
    expected_return_dic = dict()

    for char_index in range(0, num_dim):
        expected_return_dic[char_list[char_index]] = 'float'

    result = sa.run_subroutine('Template::analysis.mp', False, True, expected_return_dic)

    return HttpResponse(json.dumps({'result': result[0], 'dimensions': result[1]}))


def clear_measurement(request):
    message = sa.run_subroutine('template::clear.mp', False, True)

    return HttpResponse(message)


def run_subroutine_task(request, col_mp_name):
    message = sa.run_subroutine(col_mp_name, share_var=False, embedded=True)

    return HttpResponse(message)


def set_sa_report_tag(request, var_name, var_type, val):
    if var_type == 'str':
        sa.set_report_value_from_string(var_name, val)
    elif var_type == 'int':
        sa.set_report_value_from_integer(var_name, int(val))
    elif var_type == 'float':
        sa.set_report_value_from_double(var_name, float(val))

    return HttpResponse(True)


class HomePage(ListView):
    template_name = 'user_interface/home.html'
    model = MainFunction


class FillFormCreate(CreateView):
    model = FillForm
    template_name = 'user_interface/form.html'
    fields = ['operator',
              'tp_number',
              'flange_ref',
              'can_ref',
              'steel_temperature',
              'fabrication_stage',
              'production_machine',
              'plate_thickness',
              'passes_inside',
              'material_deposited_inside',
              'passes_outside',
              'material_deposited_outside']


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
              'flange_ref',
              'can_ref',
              'steel_temperature',
              'fabrication_stage',
              'production_machine',
              'plate_thickness',
              'passes_inside',
              'material_deposited_inside',
              'passes_outside',
              'material_deposited_outside']


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['station_name'] = FillForm.objects.get(pk=self.kwargs['pk']).station_name
        return context


def plate_inspection(request, pk):
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


def flange_fit_up(request, pk):
    fill_form_query = FillForm.objects.get(pk=pk)
    query_set = ProjectNominalAndTolerance.objects.filter(station_name=fill_form_query.station_name.pk,
                                                          flange_ref=fill_form_query.flange_ref)

    if 'lower flange' in fill_form_query.flange_ref.lower():
        template_to_load = 'lower flange fit-up'
    else:
        template_to_load =  'upper flange fit-up'

    return render(request, template_name='user_interface/inspection/flange_fit_up.html',
                  context={'form_pk': pk,
                           'template_to_load': template_to_load,
                           'required_n_tolerance_list': query_set,
                           'flange_reference': fill_form_query.flange_ref,
                           'production_machine': fill_form_query.production_machine,
                           'num_dim': len(query_set)})


def can_inspection(request, pk):
    fill_form_query = FillForm.objects.get(pk=pk)
    query_set = ProjectNominalAndTolerance.objects.filter(station_name=fill_form_query.station_name.pk,
                                                          can_ref=fill_form_query.can_ref)

    if 'before welding' in fill_form_query.fabrication_stage.lower():
        template_to_load = 'can inspection before welding'
    else:
        template_to_load =  'can inspection after welding'
    # Pass width of the plate and can reference to SA
    plate_width = ProjectNominalAndTolerance.objects.filter(station_name__name='Plate inspection',
                                                            can_ref=fill_form_query.can_ref).get(dimension_name='b').nominal

    return render(request, template_name='user_interface/inspection/can_inspection.html',
                  context={'form_pk': pk,
                           'template_to_load': template_to_load,
                           'required_n_tolerance_list': query_set,
                           'plate_width': float(plate_width),
                           'can_reference': fill_form_query.can_ref,
                           'plate_thickness': float(fill_form_query.plate_thickness),
                           'num_dim': len(query_set)})


def flange_welding_monitoring(request, pk):
    fill_form_query = FillForm.objects.get(pk=pk)
    query_set = ProjectNominalAndTolerance.objects.filter(station_name=fill_form_query.station_name.pk,
                                                          flange_ref=fill_form_query.flange_ref)

    if 'lower flange' in fill_form_query.flange_ref.lower():
        template_to_load = 'lower flange welding'
    else:
        template_to_load =  'upper flange welding'

    return render(request, template_name='user_interface/inspection/flange_welding_monitoring.html',
                  context={'form_pk': pk,
                           'template_to_load': template_to_load,
                           'required_n_tolerance_list': query_set,
                           'production_machine': fill_form_query.production_machine,
                           'num_dim': len(query_set)})


def tp_horizontal_can_fit_up(request, pk):
    fill_form_query = FillForm.objects.get(pk=pk)
    query_set = ProjectNominalAndTolerance.objects.filter(station_name=fill_form_query.station_name.pk,
                                                          flange_ref=fill_form_query.flange_ref)

    return render(request, template_name='user_interface/inspection/tp_assembled_flange_parallelism.html',
                  context={'form_pk': pk,
                           'required_n_tolerance_list': query_set,
                           'num_dim': len(query_set)})


def tp_horizontal_final(request, pk):
    fill_form_query = FillForm.objects.get(pk=pk)
    query_set = ProjectNominalAndTolerance.objects.filter(station_name=fill_form_query.station_name.pk,
                                                          flange_ref=fill_form_query.flange_ref)

    return render(request, template_name='user_interface/inspection/tp_assembled_final.html',
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

    if not win32gui.FindWindow(None, 'Overview Camera') and not win32gui.FindWindow(None, 'Untitled - Google Chrome'):
        win32gui.EnumWindows(enum_handler, None)

    return  HttpResponse()


def generate_report(request, form_pk):
    station = FillForm.objects.get(pk=form_pk).station_name.name

    if 'can' in station.lower():
        add_tolerance_to_can_dimensions(form_pk, FillForm, ProjectNominalAndTolerance)
    elif 'plate' in station.lower():
        add_tolerance_to_plate_dimensions(form_pk, FillForm, ProjectNominalAndTolerance)

    report = report_generator(form_pk, FillForm)

    return HttpResponse(report)


def sys_exit(request):
    close_app()

    return HttpResponse('')


def test(request):
    automatic_alignment(request)

    return HttpResponse('Success')

