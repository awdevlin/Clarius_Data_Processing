from hzhu_clarius import *
from input_stim_info import *


def tar_processing():
    # Data collected using Clarius Cast API

    stim_info = participant_Data().stim_info

    # Path to the file unzip_data.exe (if relative path doesn't work, use absolute)
    # lzop_path = r"..\Clarius-raw-data"

    # Path to the folder where data is stored
    # scan_folder_path = r"C:\Users\Alex Devlin\Desktop\STIM Data\STIM003\STIM003 RF Data"
    scan_folder_path = stim_info["scan_folder_path"]
    cal_lib_path = r"C:\Users\Alex Devlin\Desktop\STIM Data\Calibration Library\Ultrasound Calibration Files\C3HD3032210A0795"

    CData.csv_cleanup(scan_folder_path)

    scan_count = 0
    for scan_title in ls_file(scan_folder_path):
        if '.tar' in scan_title:
            cdata = CData(scan_folder_path, scan_title, stim_info)
            # cdata.cal_phantom_files()
            # cdata.plot_rf(0, 30, 5)
            # cdata.bmode_csv_out(1)
            if stim_info["cal_lib_search"]:
                cdata.check_cal_lib(cal_lib_path)

            print(round((scan_count + 1) / len(ls_file(scan_folder_path)) * 100, 0), '%')
        scan_count += 1


tar_processing()

# participant_Data()
