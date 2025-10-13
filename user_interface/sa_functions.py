import psutil
import logging
from lib import SAPyLib as sa
import pyautogui
import os
from pyWinActivate import win_activate


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


def sa_plate_inspection():
    sa.load_html_from_in_edge_browse(r'C:\Users\AndreyOcheretianko\Desktop\Lamprell\form.html',
                                     r'C:\Users\AndreyOcheretianko\Desktop\Lamprell\new.txt',
                                     r'C:\Users\AndreyOcheretianko\Desktop\Lamprell\new.txt',
                                     500, 500)


def close_app():
    pyautogui.shortcut('alt', 'f4')
    win_activate(window_title='Lamprell app', partial_match=True)

    pyautogui.shortcut('ctrl', 'c')
    pyautogui.shortcut('ctrl', 'c')
