import sys
from tkinter import *
from tkinter import ttk, messagebox
import psutil
import logging

from PIL.EpsImagePlugin import field

from lib import SAPyLib as sa
import threading
import pyautogui


def program_logger(log_file: str = 'Path to the txt file for logging'):
    logging.basicConfig(
        level=logging.DEBUG,
        filename=log_file,
        format="%(asctime)-12s - %(name)-8s - %(levelname)s - %(message)s",
    )

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(name)-8s - %(levelname)-8s - %(message)s"))
    logging.getLogger("").addHandler(console)

    return logging.getLogger(__name__)

def create_buttons(win, grid, name_function_dic):
    rows, columns = grid

    current_row = 0
    current_col = 0

    for name, function in name_function_dic.items():

        button = Button(win,
                        text=name,
                        font=['Arial', 55],
                        padx=40, pady=40,
                        borderwidth=5,
                        width=20, height=20,
                        command=function
                        )

        button.grid(row=current_row, column=current_col)
        win.rowconfigure(current_row, weight=1, uniform='fred')
        win.columnconfigure(current_col, weight=1, uniform='fred')

        if current_col < (columns - 1):
            current_col += 1
        else:
            current_col = 0
            current_row += 1


def warning():
    messagebox.showinfo(message='Hello, it\'s working well!')


def check_for_sa_instance():
    sa_instance_count = 0
    for proc in psutil.process_iter(['pid', 'name']):
        if 'Spatial Analyzer64.exe' == proc.info['name']:
            sa_instance_count += 1

    if not sa_instance_count:
        messagebox.showwarning(title='SA Instance', message='There is no SA started on this system. '
                                                            'Please open SA and press Ok')
        return False
    elif sa_instance_count > 1:
        messagebox.showwarning(title='SA Instance',
                               message='There are {0} SA instances started on this system. '
                                       'Please close all but 1 then press Ok'.format(sa_instance_count))
        return False
    else:
        # sa.connect_to_sa()
        return True


def app_exit():
    root.destroy()
    sys.exit()


# Plate inspection program
def plate_inspection():
    def close_new_window():
        root.deiconify()
        window.destroy()

    def fill_form_plate():
        form_window = Toplevel(root)
        form_window.state('zoomed')
        window.withdraw()

        title = Label(form_window, text="Grinding station check in form", font=('Arial', 50), justify='center')
        title.grid(row=0, columnspan=3, pady=20, padx=20, sticky=NSEW)

        labl_for_field_1 = Label(form_window, text='Operator:', font=('Arial', 20))
        labl_for_field_1.grid(column=0, row=1)

        field1 = Entry(form_window, font=('Arial', 20))
        field1.grid(column=1, row=1)

        form_window.columnconfigure(0, weight=1)
        form_window.columnconfigure(1, weight=1)
        form_window.columnconfigure(2, weight=1)

        print(field1.get())

    window = Toplevel(root)
    root.withdraw()

    fill_form_plate()

    window.title(plate_inspection.__name__.replace('_', ' ', -1).capitalize())
    window.state('zoomed')

    # MP execution in a thread
    sa.set_sa_window_state('Show')

    width, heigh = window.winfo_fpixels(window.winfo_screenwidth()), window.winfo_fpixels(
        window.winfo_screenheight())
    window.withdraw()
    sa.load_html_from_in_edge_browse(r'C:\Users\AndreyOcheretianko\Desktop\Lamprell\form.html',
                                     r'C:\Users\AndreyOcheretianko\Desktop\Lamprell\new.txt',
                                     r'C:\Users\AndreyOcheretianko\Desktop\Lamprell\new.txt',
                                     int(width), int(heigh))
    window.deiconify()
    window.state('zoomed')


    window.protocol(name='WM_DELETE_WINDOW', func=close_new_window)


# UI Starts here
root = Tk()
root.title('ALTO Growing line automation')
root.state('zoomed')

# declaring button names and MP path
buttons_functions = {
    "Plate inspection": plate_inspection,
    'Can inspection': '',
    'Bottom flange fit-up': '',
    'Top flange fit-up': '',
    'Bottom flange \nat welding station': '',
    'Top flange at \nwelding station': ''
}

# button creator
create_buttons(root, grid=[3, 2], name_function_dic=buttons_functions)

#Check for SA instance
while True:
    if check_for_sa_instance():
        break

logger = program_logger(log_file='.\\sa_sdk_log.txt')

root.protocol(name='WM_DELETE_WINDOW', func=app_exit)
root.mainloop()
