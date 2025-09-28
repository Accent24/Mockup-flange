from tkinter import *
from tkinter import ttk, messagebox
import psutil
import logging
from lib import SAPyLib as sa


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
        return True


def plate_inspection():
    def close_new_window():
        window.destroy()
        root.deiconify()

    window = Toplevel()
    window.state('zoomed')
    window.protocol(name='WM_DELETE_WINDOW', func=close_new_window)
    root.withdraw()


# UI Starts here
root = Tk()
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

logger.info('Program completed!')
root.protocol(name='WM_DELETE_WINDOW', func=root.destroy)
root.mainloop()
