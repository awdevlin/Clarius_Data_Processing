import os
import shutil
import tarfile
import csv

import clarius as cl
from threading import Lock


# This method walks through the given folder and all subsequent folders to find all .TAR files. These .TAR files
# will be unpacked and processed using the Clarius code including finding calibration data and recording results.
# A spreadsheet of the data will be saved in the root folder.
def batch_process(root_folder, calibration_folder):
    generate_report(root_folder)
    tar_file_list = find_tar_folders(root_folder)
    unpack_tar(root_folder, tar_file_list, calibration_folder)


# Unpacks .tar files, finds calibration data, and creates a spreadsheet report with the results.
def unpack_tar(root_folder, folder_paths, calibration_folder):
    report_csv = os.path.join(root_folder, "Processed Participants.csv")
    cal_lock = Lock()
    processed_count = 0
    for folder in folder_paths:
        print(f"{round(processed_count/len(folder_paths) * 100, 1)}%")
        processed_count += 1
        stim_info = {"rename_folders_cb": False}  # This keeps the file names the same as their .tar files.
        tar_filenames = ([file for file in os.listdir(folder) if ".tar" in file])
        for tar_file in tar_filenames:
            try:
                unpack = cl.CData(folder, tar_file, stim_info, cal_lock)  # tar files are unpacked when CData is created
                unpack.check_cal_lib(calibration_folder)  # save cal data in the same folder as the .tar file

                # Add calibration values to an overall report. This is different from the regular calibraiton csv
                file_name = unpack.filename[:-4]
                depth = unpack.imaging_depth()
                focus = unpack.focal_depth()
                freq = unpack.transmit_freq()
                ratio = round(float(depth[:-4]) / float(focus[:-4]), 2)
                evaluation, notes = eval_and_notes(ratio, folder, file_name)

                if file_name == "raw_0":
                    notes = notes + "Unlabelled Scan, "
                notes = notes[:-2]  # This cuts off the comma and space at the end

                line_vals = [file_name, depth, focus, freq, ratio, evaluation, notes]
                write_csv_line(report_csv, line_vals)
            except (shutil.ReadError, tarfile.ReadError, TypeError, ValueError) as e:
                write_csv_line(report_csv, [tar_file[:-4], "", "", "", "", "F", e])


# Check a few features of the scan and return the values that will go into the final report
def eval_and_notes(ratio, scan_folder, mat_ID):
    evaluation = "S"
    notes = ""
    participant_cal = os.path.join(scan_folder, "Ultrasound Calibration Data", mat_ID)

    if abs(2.0 - ratio) > 0.1:
        evaluation = "F"
        notes = notes + "Depth/Focus Off, "
    if not os.path.isdir(participant_cal):
        evaluation = "F"
        notes = notes + "Calibration Missing, "

    return evaluation, notes


# Walks through root_folder and returns a list of filepaths to all .tar files
def find_tar_folders(root_folder):
    folder_list = []
    for folder_path, dir_list, files in os.walk(root_folder):
        for file_name in files:
            if file_name.endswith(".tar"):
                folder_list.append(folder_path)
    return folder_list


# Creates a report with the scan information for each unpacked scan
def generate_report(walk_dir):
    processed_data_report = os.path.join(walk_dir, "Processed Participants.csv")
    delete_csv(processed_data_report)

    with open(processed_data_report, 'a', newline='') as report_csvfile:
        writier = csv.writer(report_csvfile, delimiter=",")
        writier.writerow(["Maternal ID", "Depth", "Focus Frequency", "Tx", "Depth/Focus", "Cal Success/Fail", "Notes"])


# Adds the maternal ID and scan details to the report CSV
def update_report(report_path):
    with open(report_path, newline='') as csvfile:
        cal_reader = csv.reader(csvfile, quotechar='|')
        for row in cal_reader:
            if "Scan name" not in row:  # Skip the header row at the top
                write_csv_line(report_path, row)


# Checks if a file exists and removes it
def delete_csv(csv_title):
    if os.path.exists(csv_title):
        os.remove(csv_title)


# Adds a new line to a csv file. new_line must be given as a list of values. If given a string, each letter from the
# string will be split up as its own value. e.g. Apple -> a,p,p,l,e
def write_csv_line(csv_name, new_line):
    with open(csv_name, 'a', newline='') as csvfile:
        writier = csv.writer(csvfile, delimiter=",")
        writier.writerow(new_line)


root = r"E:\Clarius Expansion Data\WUSTL Clarius\2025-01-06"
cal_folder = r"E:\Calibration Library\BCWMain New Cal Phantom"
batch_process(root, cal_folder)

