import psutil
import logging
from lib import SAPyLib as sa
import pyautogui
import os
from pyWinActivate import win_activate
import json


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


def open_template_check_connection(template_name):
    collection_name = 'Inspection'
    instrument_id = 0
    template_path = os.path.join(r'C:\Users\AndreyOcheretianko\Desktop\Lamprell', template_name + '.xit64')
    sa.open_sa_file(template_path)
    # sa.set_sa_window_state('Hide')

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
    pyautogui.shortcut('alt', 'f4')
    win_activate(window_title='Lamprell app', partial_match=True)

    pyautogui.shortcut('ctrl', 'c')
    pyautogui.shortcut('ctrl', 'c')
