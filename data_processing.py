from clarius import *
from input_stim_info import *


def tar_processing():
    # Data collected using Clarius Cast API

    stim_info = participant_Data().stim_info

    # Path to the folder where data is stored
    # cal_lib_path = r"C:\Users\Alex Devlin\Desktop\STIM Data\Calibration Library\Ultrasound Calibration Files\C3HD3032210A0795"
    scan_folder_path = stim_info["scan_folder_path"]

    CData.csv_cleanup(scan_folder_path)

    scan_count = 0
    for scan_title in ls_file(scan_folder_path):
        if '.tar' in scan_title:
            cdata = CData(scan_folder_path, scan_title, stim_info)
            if stim_info["collecting_cal_data"]:
                cdata.cal_phantom_files()
            if stim_info["b-mode_plot"]:
                cdata.plot_rf()
            if stim_info["cal_lib_path"]:
                cdata.check_cal_lib(stim_info["cal_lib_path"])

            print(round((scan_count + 1) / len(ls_file(scan_folder_path)) * 100, 0), '%')
        scan_count += 1


tar_processing()
