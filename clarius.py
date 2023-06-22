import shutil
from subprocess import run
import numpy as np
from scipy.signal import hilbert
import matplotlib.pyplot as plt
import rdataread as rd
import yaml
import csv

from hzhu_gen import *


# Data type that processes the ultrasound scan information from a Clarius probe. This data will
# be in .TAR format initially. It will be unpacked into .RAW, .YAML, and .TGC files automatically
# when a new CData object is created.
class CData:
    def __init__(self, folder_path, filename, stim_info, lzop_path=os.getcwd()):
        self.folder_path = folder_path
        self.filename = filename
        self.lzop_path = lzop_path
        self.folder_name = os.path.join(self.folder_path, *filename.split('.')[0:-1])
        self.project_site, self.maternal_id, self.gestational_age, self.image_num = \
            stim_info["project_site"], stim_info["maternal_id"], stim_info["gestational_age"], stim_info["image_num"]
        self.fetal_num, self.raw_or_rend = stim_info["fetal_num"], stim_info["raw_or_rend"]
        self.stim_filename = "_".join([self.project_site, self.maternal_id, self.fetal_num, self.gestational_age,
                                       self.__remove_file_type(self.filename), self.image_num, self.raw_or_rend])
        self.folder_name = os.path.join(self.folder_path, self.stim_filename)
        shutil.unpack_archive(os.path.join(self.folder_path, filename), self.folder_name)
        self.files = ls_file(self.folder_name)
        for item in self.files:
            if '.raw.lzo' in item:
                run(
                    '\"%s\\unzip_data.exe\" -d \"%s\"' % (self.lzop_path, os.path.join(self.folder_name, item)),
                    shell=True)
                os.remove(os.path.join(self.folder_name, item))
        self.files = ls_file(self.folder_name)
        self.hdr, timestamps, self.data = self.get_rf()
        self.num_frames = self.hdr['frames']
        self.__cal_val_csv()
        print('Loaded {d[2]} raw frames of size, {d[0]} x {d[1]} (lines x samples)'.format(d=self.data.shape))

    # If there is a file that ends in "rf.raw" in the current folder, this function returns the information about
    # that file. Returned values: hdr, timestamps, data. hdr contains 'lines', 'samples', and 'frames'
    def get_rf(self):
        for item in self.files:
            if 'rf.raw' in item:
                return rd.read_rf(os.path.join(self.folder_name, item))
        return None

    # Displays several b-mode images from the data frame. step is the number of frames that
    # are skipped between each displayed image. There can be a lot so don't set this too low
    def plot_rf(self, start=1000, stop=float('inf'), step=1000):
        hdr = self.hdr
        data = self.data
        stop = min(hdr['frames'], stop)
        if start > self.num_frames - 1:
            start = self.num_frames - 1

        # convert to B-mode
        bdata = np.zeros((hdr['lines'], hdr['samples'], hdr['frames']), dtype='float')
        for frame in range(start, stop, step):
            bdata[:, :, frame] = 20 * np.log10(np.abs(1 + hilbert(data[:, :, frame])))

        # display images
        for frame in range(start, stop, step):
            plt.figure(figsize=(10, 5))
            plt.subplot(1, 2, 1)
            plt.imshow(np.transpose(data[:, :, frame]), cmap=plt.cm.gray, aspect='auto', vmin=-1000, vmax=1000)
            plt.title('RF frame ' + str(frame + 1))
            plt.subplot(1, 2, 2)
            plt.imshow(np.transpose(bdata[:, :, frame]), cmap=plt.cm.gray, aspect='auto', vmin=15, vmax=70)
            plt.title(self.__remove_file_type(self.filename) + ' frame ' + str(frame + 1))
            plt.show()

    # Generates a .CSV file from the b-mode data frames downloaded from the Clarius probe
    # Frames are generated in reverse order because the b-mode is paused when you see
    # an area of interested. The first few frames are often used for landmarking
    def bmode_csv_out(self, total_frames):
        data = self.data
        name = self.__remove_file_type(self.filename)
        start_frame = self.num_frames - total_frames
        # Prevents the user from asking for too many frames. Displays them all instead.
        if start_frame < 0:
            start_frame = 0
            total_frames = self.num_frames
        for frame in range(total_frames):
            file_name = name + " frame {}.csv".format(start_frame + frame)
            if os.path.isfile(os.path.join(self.folder_name, file_name)):
                print(".CSV RF data file already exists")
            else:
                scan_info_header = self.__yaml_header()
                np.savetxt(os.path.join(self.folder_name, file_name),
                           np.transpose(data[:, :, frame]), delimiter=",", header=scan_info_header)
                print(round((frame + 1) / total_frames * 100, 0), '%')

    # Returns all data frames as .CSV. No need to specify number.
    def csv_all_frames(self):
        self.bmode_csv_out(self.num_frames)

    # Generates a list of parameters of the scan. Creates a header for the CSV file using the yaml file information. The
    # output is separated by commas to work with .CSV format
    def __yaml_header(self):
        yaml_info = self.__yaml_info()
        imaging_depth = yaml_info["imaging depth"]
        focal_depth = yaml_info["focal depth"]
        tgc = yaml_info["tgc"]
        full_header = "," + "imaging depth" + "," + imaging_depth + "," + "focal_depth," + focal_depth + "," + "tgc,"

        # the TGC values are stored as keys. This reads those keys. I don't think they map to any useful information
        for depth in tgc:
            for key in depth:
                full_header = full_header + key + ","
        return full_header

    # Returns the details of the probe and the scan by reading the .yml file downloaded from Clarius Cast
    def __yaml_info(self):
        folder_path = self.folder_name
        rf_yml_file_name = ''
        for item in self.files:
            if 'rf.yml' in item:
                rf_yml_file_name = item.title()
        with open(os.path.join(folder_path, rf_yml_file_name)) as file:
            yaml_info = yaml.safe_load(file)
        return yaml_info

    # Generates a name for the calibration file by looking for 0_54 or 1_30 in the file name. These values come
    # from the two different regions of the attenuation phantom. Units: dB/cm/MHz
    def __cal_details(self):
        name = self.stim_filename
        yaml_info = self.__yaml_info()
        attenuation = '0_00'
        if '0_54' in name:
            attenuation = '0_54'
        elif '1_30' in name:
            attenuation = '1_30'
        else:
            print("Incorrect Attenuation Values")
        file_name = "D{} F{}".format(yaml_info["imaging depth"], yaml_info["focal depth"])
        return file_name, attenuation

    def cal_phantom_files(self):
        self.__cal_raw()
        self.__cal_tgc()
        self.__cal_yaml()

    # searches for the strings found in the list called search. If a files contains one of these strings,
    # it is copied and labeled with the calibration information
    # Search must be a list even if it is size one
    def __cal_copy(self, search):
        filename, attenuation = self.__cal_details()
        cal_path = os.path.join(self.folder_path, "Ultrasound Calibration Phantom")
        filename_path = os.path.join(cal_path, filename)
        attenuation_path = os.path.join(filename_path, attenuation)
        self.create_folder(cal_path)
        self.create_folder(filename_path)
        self.create_folder(attenuation_path)
        for s in search:
            for item in ls_file(self.folder_name):
                if s in item:
                    shutil.copyfile(os.path.join(self.folder_name, item),
                                    os.path.join(attenuation_path, filename + " " + s))

    #  Copy yml files and renames them to match the calibration file with depth, focus, and attenuation values
    def __cal_raw(self):
        self.__cal_copy(["rf.raw", "env.raw"])

    # Copy yml files and renames them to match the calibration file with depth, focus, and attenuation values
    def __cal_yaml(self):
        self.__cal_copy(["rf.yml", "env.yml"])

    # Copy tgc files and renames them to match the calibration file with depth, focus, and attenuation values
    def __cal_tgc(self):
        self.__cal_copy(["env.tgc"])

    # Creates a .CSV file for calibration purposes. Generates the filename based on the depth, focus, and
    # attenuation values of the scan. Attenuation is read from the file name. Ensure 0_54 or 1_30 is
    # included in the file name.
    def cal_csv(self):
        data = self.data
        start_frame = self.num_frames
        scan_info_header = self.__yaml_header()
        filename = self.__cal_details()[0] + ".csv"
        if os.path.isfile(os.path.join(self.folder_name, filename)):
            print(".CSV RF data file already exists")
        else:
            np.savetxt(os.path.join(self.folder_name, filename),
                       np.transpose(data[:, :, start_frame - 1]), delimiter=",", header=scan_info_header)

    # Creates a CSV file with the depth and focus of the scan. If multiple scans are processed, it appends these
    # values to the bottom of the CSV.
    def __cal_val_csv(self):
        csv_title = "Ultrasound Depth and Focus"
        cal_folder = os.path.join(self.folder_path, "Ultrasound Calibration Data")
        self.create_folder(cal_folder)
        file_name = os.path.join(cal_folder, csv_title + ".csv")
        self.__add_cal_line(file_name)

    # Adds a new line to a CSV file. If this is the first line added to the CSV, it creates headers.
    def __add_cal_line(self, file_name):
        if not os.path.exists(file_name):  # If this is the first line added, it also creates headers
            header_vals = ["Scan name", "Depth", "Focus"]
            self.new_csv_line(file_name, header_vals, 'w')
        yaml_info = self.__yaml_info()
        depth, focus = yaml_info["imaging depth"], yaml_info["focal depth"]
        csv_cal_vals = [self.__remove_file_type(self.filename), self.__remove_mm(depth), self.__remove_mm(focus)]
        self.new_csv_line(file_name, csv_cal_vals)

    # Adds a new row to the end of a CSV file. Appends by default. Mode can be changed for write, create, etc
    @staticmethod
    def new_csv_line(file_name, line_vals, mode='a'):
        with open(file_name, mode, newline='') as csv_out:  # newline = '' is needed or you get spaces between lines
            cal_writer = csv.writer(csv_out)
            cal_writer.writerow(line_vals)
            csv_out.close()

    # Searches the calibration library to check if the data has already been captured
    def check_cal_lib(self, cal_lib_path, delta=0.5):
        depth = self.__remove_mm(self.__yaml_info()['imaging depth'])
        depth_lib = ls_dir(cal_lib_path)
        closest_value = []
        max_diff = float("inf")
        for lib_search in depth_lib:
            lib_search = self.__remove_focus(lib_search)
            try:
                difference = abs(float(lib_search) - float(depth))
            except ValueError:
                continue
            if difference < delta and difference < max_diff:  # The header will read depth, but we only want the numbers
                max_diff = difference
                closest_value = difference, lib_search
        if not closest_value:  # If no calibration value within delta of the measured value, add it to not found list
            csv_title = "Ultrasound Depth and Focus Not Found"
            cal_folder = os.path.join(self.folder_path, "Ultrasound Calibration Data")
            file_name = os.path.join(cal_folder, csv_title + ".csv")
            self.__add_cal_line(file_name)
        else:
            self.__copy_cal_files(closest_value[1], cal_lib_path)

    def __copy_cal_files(self, depth_val, cal_lib_path):
        cal_folder = os.path.join(self.folder_path, "Ultrasound Calibration Data")
        copy_location = os.path.join(self.folder_path, cal_folder)
        self.create_folder(cal_folder)
        for folder in ls_dir(cal_lib_path):
            depth_path = os.path.join(copy_location, self.__remove_file_type(self.filename))
            if depth_val in folder and not os.path.exists(depth_path):
                shutil.copytree(os.path.join(cal_lib_path, folder), depth_path)

    # Removes an affix of length "suffix_len" from the end of a filename. EG __remove_affix("text.csv", 4) -> "text"
    # Also remove any whitespace at the start and end of the file name to prevent issues with folder naming
    @staticmethod
    def __remove_file_type(file_name):
        return file_name.split('.')[0:-1][0].strip()

    # Removes " mm" (including the space) from the end of a file name. EG "55.55 mm" -> "55.55"
    @staticmethod
    def __remove_mm(measurement):
        return measurement[0:-3]

    # Given the format for Depth and Focus, D94.50 mm F47.23 mm. Prints only the first number. EG returns 94.50
    @staticmethod
    def __remove_focus(depth_and_focus):
        return depth_and_focus[1:depth_and_focus.find(' mm')]

    # Deletes the old CSV files that that show which calibration data is there and is still missing
    @staticmethod
    def csv_cleanup(scan_folder_path):
        cal_folder = "Ultrasound Calibration Data"
        found_cal_files = os.path.join(scan_folder_path, cal_folder, "Ultrasound Depth and Focus.csv")
        missing_cal_files = os.path.join(scan_folder_path, cal_folder, "Ultrasound Depth and Focus Not Found.csv")
        CData.remove_folder(found_cal_files)
        CData.remove_folder(missing_cal_files)

    @staticmethod
    def create_folder(folder_path):
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

    @staticmethod
    def remove_folder(folder_path):
        if os.path.isfile(folder_path):
            os.remove(folder_path)
