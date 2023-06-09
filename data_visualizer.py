from hzhu_clarius import *

# Data collected using Clarius Cast API

# Path to the file unzip_data.exe (if relative path doesn't work, use absolute)
# lzop_path = r"..\Clarius-raw-data"
# This path to unzip_data.exe will only work if the file is located in the same folder as this one
lzop_path = os.getcwd()

# Path to the folder where data is stored
scan_folder_path = r"C:\Users\Alex Devlin\Desktop\STIM Data\STIM002\STIM002 Calibration Attenuation Phantom"
cal_lib_folder_path = r"C:\Users\Alex Devlin\Desktop\Calibration Library\Ultrasound Calibration Files\C3HD3032210A0795"

CData.csv_cleanup(scan_folder_path)

stim_info = {
    "maternal_id": "STIM009",
    "gestational_age": "13.6",
    "project_site": "5",
    "fetal_num": "1",
    "image_num": "1",
    "raw_or_rend": "raw"
}

scan_count = 0
for scan_title in ls_file(scan_folder_path):
    if '.tar' in scan_title:
        cdata = CData(scan_folder_path, scan_title, stim_info)
        cdata.cal_files()
        # cdata.plot_rf(0, 30, 5)
        cdata.check_cal_files(cal_lib_folder_path)

        print(round((scan_count + 1) / len(ls_file(scan_folder_path)) * 100, 0), '%')
    scan_count += 1



