import sys
import os
import logging

# Base path to the SDK Lib
BASE_PATH = r"C:\Users\Andrey Ocheretianko\PycharmProjects\SA Automation"
LOG_FILE = os.path.join(BASE_PATH, "sa_sdk_log.txt")

# Add the directory containing SAPyLib.py to the path and setting up logging
sys.path.append(os.path.join(BASE_PATH, "lib"))
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)

# importing the SDK library and catching import error
try:
    from lib import SAPyLib as sa
    logging.info("SAPyLib imported successfully.")
except ModuleNotFoundError as e:
    logging.error(f"Error importing SAPyLib: {e}")
    print(f"Error importing SAPyLib: {e}")

# Logging set-up
lib_path = os.path.join(BASE_PATH, "lib")

logging.basicConfig(
    level=logging.DEBUG,
    filename=LOG_FILE,
    format="%(asctime)-12s - %(name)-8s - %(levelname)s - %(message)s",
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter("%(name)-8s - %(levelname)-8s - %(message)s"))
logging.getLogger("").addHandler(console)
log = logging.getLogger(__name__)

sa.open_sa_file(r"C:\Users\Andrey Ocheretianko\Desktop\default 2025.09.20 13.40.xit64")

# Set the SA interaction mode
sa.set_interaction_mode(sa_interaction_mode="Silent",
                        mp_interaction_mode="Never Halt",
                        mp_dialog_interaction_mode="Block Application Interaction")

sa.run_subroutine(path="C:\\Users\\Andrey Ocheretianko\\Desktop\\test_plane.mp",
                  share_var=False)

# Exit the program and resource release
log.info("Program completed!")
sys.exit(0)
