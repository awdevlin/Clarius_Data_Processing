from clarius import *
# from input_stim_info import *


# Processes all .tar files in the folder located at scan_folder_path.
def tar_processing(stim_info):
    # Data collected using Clarius Cast API

    # Path to the folder where data is stored
    scan_folder_path = stim_info["scan_folder_path"]

    scan_count = 0
    for scan_title in ls_file(scan_folder_path):
        if '.tar' in scan_title:
            cdata = CData(scan_folder_path, scan_title, stim_info)
            if scan_count == 0:  # Delete old files on the first loop. Need CData object to be created first
                cdata.csv_cleanup(scan_folder_path)

            # Determinte which functions are run based on which check boxes are selected
            if stim_info["collecting_cal_data"]:
                cdata.cal_phantom_files()
            if stim_info["b-mode_plot"]:
                cdata.plot_rf()
            if stim_info["cal_lib_path"]:
                cdata.check_cal_lib(stim_info["cal_lib_path"])

            # print(scan_title + " " + cdata.transmit_freq())

        # Print progress based on how many files are processed. Visual feedback for long scans.
        print(round((scan_count + 1) / len(ls_file(scan_folder_path)) * 100, 0), '%')
        scan_count += 1
