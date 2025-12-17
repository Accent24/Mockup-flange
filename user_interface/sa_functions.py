import psutil
from lib import SAPyLib as sa
import os


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

    sa.open_sa_file(template_path)
    # sa.set_sa_window_state('Hide')
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
        target_type = 'Set Targ Scan Target: 1.5" Scan sphere'
    else:
        target_type = 'Set Targ Retro: Surface'

    sa.instrument_operational_check(collection_inst=collection, id_inst=0, check_type='ADM Reset')
    sa.instrument_operational_check(collection_inst=collection, id_inst=0, check_type=target_type)
    result = sa.configure_and_measure(collection_inst=collection, id_inst=0,
                                       collection_target=collection, group_target=group, name_target=name,
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

    base_dir = os.path.join(base_dir, 'Reports', 'TP{0} {1} {2}'.format(query_object.tp_number,
                                                                              query_object.can_ref,
                                                                              query_object.date_time.strftime('%d-%m-%Y %H-%M')))

    if not os.path.isdir(base_dir):
        os.mkdir(base_dir)

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

    report_number = 'CN/24/2106/HAM/GL/PL/TP{0}/{1}/DC{2}'.format(query_object.tp_number, query_object.can_ref,
                                                                  current_report_index)
    report_tags = {'Tp': str(query_object.tp_number),
                   'Can': query_object.can_ref,
                   'Operator': query_object.operator.full_name,
                   'Temperature': str(query_object.steel_temperature),
                   'Report number': report_number}

    for k, v in report_tags.items():
        sa.set_report_value_from_string(k, v)

    file_path = os.path.join(base_dir, '{0}.pdf'.format(report_number.replace('/', '_')))
    sa.output_SA_report_to_PDF('Report',
                               'Report',
                               file_path,
                               False)

    static_path_for_preview = os.path.join(os.path.basename(base_dir), os.path.basename(file_path))
    return static_path_for_preview

list_of_cans = [('MS-CN1', 'MS-CN1'),
                ('MS-CN2', 'MS-CN2'),
                ('MS-CN3', 'MS-CN3'),
                ('MS-CN4', 'MS-CN4'),
                ('MS-CN5', 'MS-CN5'),
                ('MS-CN6', 'MS-CN6')]

list_of_stages = [('After welding', 'After welding'),
                  ('After fit-up', 'After fit-up'),
                  ('Welding in progress', 'Welding in progress'),
                  ('Plate after grinding', 'Plate after grinding')]