import psutil
from lib import SAPyLib as sa
import os

from lib.SAPyLib import set_dimension_tolerance


def check_for_sa_instance():
    sa_instance_count = 0
    message = None
    for proc in psutil.process_iter(['pid', 'name']):
        if 'Spatial Analyzer64.exe' == proc.info['name']:
            sa_instance_count += 1

    if not sa_instance_count:
        message = 'There is no SA started on this system. Please open SA and press "Retry" button'
        return False, message
    elif sa_instance_count > 1:
        message= 'There are {0} SA instances started on this system. Please close all but 1 then press "Retry" button'.format(sa_instance_count)
        return False, message
    else:
        sa.connect_to_sa()
        return True, message


def check_for_instrument_connection():
    if bool(sa.verify_instrument_connection('', 0)):
        return True
    else:
        return False


def open_template_check_connection(template_name):
    collection_name = 'Inspection'
    instrument_id = 0
    template_path = os.path.join(os.path.abspath('.\SA_templates'), template_name + '.xit64')
    # TODO: Remove comment before deployment
    sa.open_sa_file(template_path)
    sa.set_sa_window_state('Hide')
    sa.set_interaction_mode('Automatic', 'Never Halt', 'Allow Application Interaction')
    sa.start_instrument_interface(collection_name, instrument_id, initialize=False)

    if bool(sa.verify_instrument_connection(collection_name, instrument_id)):
        return True
    else:
        return False


def measure_pt(collection, group, name, target_type):
    if target_type == 'smr':
        target_type = 'Set Targ SMR: RRR 1.5in'
    elif target_type == 'sphere':
        target_type = 'Set Targ Scan Target: scan sphere'
    else:
        target_type = 'Set Targ Retro: Surface'

    sa.stop_active_measurement_mode(collection_inst=collection, id_inst=0)
    sa.set_instrument_measurement_mode_profile(collection_inst=collection, id_inst=0, mode_profile='Fast Pt. To SA')
    sa.instrument_operational_check(collection_inst=collection, id_inst=0, check_type=target_type)

    if 'SMR' in target_type:
        sa.instrument_operational_check(collection_inst=collection, id_inst=0, check_type='ADM Reset')

    if name == ' ':
        if sa.object_existence_test(collection, group):
            name = sa.get_number_of_points_in_group(collection, group) + 1
        else:
            name = 1

    result = sa.configure_and_measure(collection_inst=collection, id_inst=0,
                                      collection_target=collection, group_target=group, name_target=str(name),
                                      profile_name='Fast Pt. To SA', measure_immediately=True, wait_for_completion=True,
                                      timeout_in_secs=0.0)

    return result


def close_app():
    collection = 'Inspection'
    instrument_id = 0

    instrument = sa.get_instrument_model(instrument_id)

    if not 'api' in instrument.lower():
        if sa.verify_instrument_connection(collection, instrument_id):
            sa.instrument_operational_check(collection, instrument_id, 'Shut Down Tracker')
        else:
            sa.start_instrument_interface(collection, instrument_id, False)
            sa.instrument_operational_check(collection, instrument_id, 'Shut Down Tracker')

    os.system('shutdown /s')


def cancel_measurement_and_start_new(col, group, profile_name):
    sa.stop_active_measurement_mode(col, 0)
    sa.instrument_operational_check(collection_inst=col, id_inst=0, check_type='Set Targ SMR: RRR 1.5in')

    while True:
        result = sa.configure_and_measure(collection_inst=col, id_inst=0, collection_target=col, group_target=group,
                                          name_target='1', profile_name=profile_name, measure_immediately=True,
                                          wait_for_completion=False, timeout_in_secs=5)
        if result:
            break


def report_generator(form_pk, fill_form_model):
    sa.run_subroutine("Template::report.mp", True, True)

    query_object = fill_form_model.objects.get(pk=form_pk)

    # prep folders for report
    base_dir = os.path.abspath('../')
    if not os.path.isdir(os.path.join(base_dir, 'Reports')):
        os.mkdir(os.path.join(base_dir, 'Reports'))

    station_name = query_object.station_name.name
    can_reference = False
    if 'plate' in station_name.lower():
        station_name = 'PL'
        can_reference = True
    elif 'can' in station_name.lower():
        station_name = 'CAN'
        can_reference = True
    elif 'flange' in station_name.lower() and 'lower' in station_name.lower():
        station_name = 'LF'
    elif 'flange' in station_name.lower() and 'upper' in station_name.lower():
        station_name = 'UF'
    elif query_object.flange_ref and 'lower' in query_object.flange_ref.lower():
        station_name = 'LF'
    elif query_object.flange_ref and 'upper' in query_object.flange_ref.lower():
        station_name = 'UF'
    else:
        station_name = 'GL'

    if can_reference:
        base_dir = os.path.join(base_dir, 'Reports', 'TP{0} {1} {2} {3}'.format(query_object.tp_number,
                                                                                  query_object.can_ref,
                                                                                  station_name,
                                                                                  query_object.date_time.strftime('%d-%m-%Y %H-%M')))
    else:
        base_dir = os.path.join(base_dir, 'Reports', 'TP{0} {1} {2}'.format(query_object.tp_number,
                                                                                  station_name,
                                                                                  query_object.date_time.strftime('%d-%m-%Y %H-%M')))

    if not os.path.isdir(base_dir):
        os.mkdir(base_dir)

    sa.refresh_callout_view_in_report('Report', 'Report')
    report_numbering_file = os.path.join(os.path.split(base_dir)[0], 'report_numbering.txt')

    current_report_index = ''
    if not os.path.isfile(report_numbering_file):
        with open(report_numbering_file, 'w') as file_write:
            file_write.write(str(form_pk) + ', ' + str(1) + '\n')
            current_report_index = str(1)
    else:
        with open(report_numbering_file) as file_read:
            last_line = file_read.readlines()[-1].strip('\n').split(',')

            if not int(last_line[0]) == form_pk:
                current_report_index = str(int(last_line[1]) + 1)

                with open(report_numbering_file, 'w') as file_write:
                    file_write.write(str(form_pk) + ', ' + str(current_report_index) + '\n')
            else:
                current_report_index = last_line[1].strip(' ')

    if len(current_report_index) == 1:
        current_report_index = '00' + current_report_index
    elif len(current_report_index) == 2:
        current_report_index = '0' + current_report_index
    else:
        current_report_index = current_report_index

    if can_reference:
        report_number = 'CN/24/2106/HAM/GL/{0}/TP{1}/{2}/DC{3}'.format(station_name, query_object.tp_number,
                                                                       query_object.can_ref, current_report_index)
    else:
        report_number = 'CN/24/2106/HAM/GL/{0}/TP{1}/DC{2}'.format(station_name, query_object.tp_number,
                                                                   current_report_index)

    report_tags = {'Tp': str(query_object.tp_number),
                   'Can': query_object.can_ref,
                   'Operator': query_object.operator.full_name,
                   'Temperature': str(query_object.steel_temperature),
                   'Report number': report_number,
                   'Production machine': query_object.production_machine,
                   'Inside pass': str(query_object.passes_inside),
                   'Outside pass': str(query_object.passes_outside),
                   'Material inside': str(query_object.material_deposited_inside),
                   'Material outside': str(query_object.material_deposited_outside)}

    for k, v in report_tags.items():
        sa.set_report_value_from_string(k, v)

    file_path_pdf = os.path.join(base_dir, '{0}.pdf'.format(report_number.replace('/', '_')))
    # Exporting PDF
    sa.output_SA_report_to_PDF('Report',
                               'Report',
                               file_path_pdf,
                               False)

    # Saving the file for reference
    file_path_sa = os.path.join(base_dir, '{0}.xit64'.format(report_number.replace('/', '_')))
    sa.save_as(file_path_sa)

    # Pop up with report
    static_path_for_preview = os.path.join(os.path.basename(base_dir), os.path.basename(file_path_pdf))
    return static_path_for_preview


def add_tolerance_to_plate_dimensions(form_pk, fill_form_model, project_tolerance_model):
    # get all the dimension tolerances applied to the plate
    fill_form_query = fill_form_model.objects.get(pk=form_pk)
    query_set = project_tolerance_model.objects.filter(station_name=fill_form_query.station_name.pk,
                                                       can_ref=fill_form_query.can_ref)

    collection, callout_name = 'Report', 'Dimension'

    sa.show_hide_callout_view(collection, callout_name, True)
    callout_positions = {'a': [0.443, 0.814], 'b': [0.87, 0.5], 'c': [0.44, 0.22], 'd': [0.0, 0.5],
                         'e': [0.308, 0.565], 'f': [0.598, 0.565]}

    for dimension in query_set:
        if not dimension.dimension_name.lower() in ['g', 'h', 'i', 'j']:
            sa.set_dimension_tolerance('Template', dimension.dimension_name.lower(), dimension.nominal,
                                       dimension.tolerance_upper, dimension.tolerance_lower)

            sa.create_text_callout(collection, callout_name, 'Required: {0} +/-{1}'.format(dimension.nominal,
                                                                                          dimension.tolerance_upper),
                                   callout_positions[dimension.dimension_name.lower()][0],
                                   callout_positions[dimension.dimension_name.lower()][1])


def add_tolerance_to_can_dimensions(form_pk, fill_form_model, project_tolerance_model):
    fill_form_query = fill_form_model.objects.get(pk=form_pk)
    query_set = project_tolerance_model.objects.filter(station_name=fill_form_query.station_name.pk,
                                                       can_ref=fill_form_query.can_ref)

    collection = 'Report'
    relationship_name = ''

    for dimension in query_set:
        if dimension.dimension_name.lower() == 'a':
            relationship_name = 'Bottom circumference'
        elif dimension.dimension_name.lower() == 'b':
            relationship_name = 'Top circumference'

        sa.set_geom_relationship_criteria(collection, relationship_name, 'Length', dimension.tolerance_upper,
                                          dimension.tolerance_lower)
        sa.set_report_value_from_string('Can', fill_form_query.can_ref)


list_of_cans = [('MS-CN1', 'MS-CN1'),
                ('MS-CN2', 'MS-CN2'),
                ('MS-CN3', 'MS-CN3'),
                ('MS-CN4', 'MS-CN4'),
                ('MS-CN5', 'MS-CN5'),
                ('MS-CN6', 'MS-CN6')]

list_of_stages = [('After welding', 'After welding'),
                  ('After fit-up', 'After fit-up'),
                  ('Welding in progress', 'Welding in progress'),
                  ('CAN Before welding', 'CAN Before welding'),
                  ('CAN After welding', 'CAN After welding'),
                  ('Plate after grinding', 'Plate after grinding')]

list_of_machines = [('SATO 38x8000_1336/CC0039', 'SATO 38x8000_1336/CC0039'),
                    ('SATO 38x6000_1337/CC0041', 'SATO 38x6000_1337/CC0041'),
                    ('Welding station A', 'Welding station A'),
                    ('Welding station B', 'Welding station B'),
                    ('Welding station C', 'Welding station C'),
                    ('Welding station D', 'Welding station D'),
                    ('Welding station E', 'Welding station E'),
                    ('Welding station F', 'Welding station F'),
                    ('Welding station G', 'Welding station G'),
                    ('Welding station H', 'Welding station H')]

list_of_flanges = [('Upper flange', 'Upper flange'),
                  ('Lower flange', 'Lower flange')]