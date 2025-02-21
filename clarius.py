from hzhu_gen import *

import shutil
from subprocess import run
import numpy as np
from scipy.signal import hilbert
import matplotlib.pyplot as plt
import rdataread as rd
import yaml
import csv


# Data type that processes the ultrasound scan information from a Clarius probe. This data will
# be in .TAR format initially. It will be unpacked into .RAW, .YAML, and .TGC files automatically
# when a new CData object is created.
# noinspection PyTypeChecker
class CData:
    def __init__(self, folder_path, filename, stim_info, lock=None, lzop_path=os.getcwd()):
        self.folder_path = folder_path
        self.filename = filename
        self.lzop_path = lzop_path

        if stim_info["rename_folders_cb"]:
            self.project_site, self.maternal_id, self.gestational_age, self.image_num = \
                stim_info["project_site"], stim_info["maternal_id"], stim_info["gestational_age"], stim_info["image_num"]
            self.fetal_num = stim_info["fetal_num"]

            self.stim_filename = "_".join([self.project_site, self.maternal_id, self.fetal_num, self.gestational_age,
                                           self.__remove_file_type(self.filename), self.image_num])

        if not stim_info["rename_folders_cb"]:
            self.stim_filename = self.__remove_file_type(self.filename)
            # self.stim_filename = self.filename  # Replace the previous line with this to process .dir instead of .tar

        self.folder_name = os.path.join(self.folder_path, self.stim_filename)
        print(self.stim_filename)
        print(f"folder_name: {self.folder_name}")

        # Comment out this line with this to process .dir instead of .tar
        shutil.unpack_archive(os.path.join(self.folder_path, filename), self.folder_name)  # unzips the .tar files

        self.cal_folder_name = "Ultrasound Calibration Data"
        self.cal_csv_name = "Ultrasound Depth and Focus"
        self.files = ls_file(self.folder_name)
        for item in self.files:
            if '.raw.lzo' in item:
                run('\"%s\\unzip_data.exe\" -d \"%s\"' % (self.lzop_path, os.path.join(self.folder_name, item)),
                    shell=True)
                os.remove(os.path.join(self.folder_name, item))
        self.files = ls_file(self.folder_name)
        self.hdr, timestamps, self.data = self.get_rf()
        self.num_frames = self.hdr['frames']
        self.cal_lock = lock
        self.__cal_val_csv()
        print('Loaded {d[2]} raw frames of size, {d[0]} x {d[1]} (lines x samples)'.format(d=self.data.shape))

    # If there is a file that ends in "rf.raw" in the current folder, this function returns the information about
    # that file. Returned values: hdr, timestamps, data. hdr contains 'lines', 'samples', and 'frames'
    def get_rf(self):
        for item in self.files:
            if 'rf.raw' in item:
                return rd.read_rf(os.path.join(self.folder_name, item))
        print('RF data missing')
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
            plt.imshow(np.transpose(data[:, :, frame]), cmap='gray', aspect='auto', vmin=-1000, vmax=1000)
            plt.title('RF frame ' + str(frame + 1))
            plt.subplot(1, 2, 2)
            plt.imshow(np.transpose(bdata[:, :, frame]), cmap='gray', aspect='auto', vmin=15, vmax=70)
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
            self.__save_csv(file_name, data, frame)

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
        full_header = ",".join(["", "imaging depth", imaging_depth, "focal_depth", focal_depth, "tgc", ""])

        # the TGC values are stored as keys. This reads those keys. I don't think they map to any useful information
        for depth in tgc:
            for key in depth:
                full_header = full_header + key + ","
        return full_header

    # Returns the details of the probe and the scan by reading the .yml file downloaded from Clarius Cast
    def __yaml_info(self, folder_path=''):
        if folder_path == '':
            folder_path = self.folder_name
            files = self.files
        else:
            files = ls_file(folder_path)

        rf_yml_file_name = ''
        for item in files:
            if 'rf.yml' in item:  # Checks the YAML file for the RF data, not the B-mode
                rf_yml_file_name = item.title()
        with open(os.path.join(folder_path, rf_yml_file_name)) as file:
            yaml_info = yaml.safe_load(file)
        return yaml_info

    # Generates a name for the calibration file by looking for 0_50 or 1_20 in the file name. These values come
    # from the two different regions of the attenuation phantom. Units: dB/cm/MHz
    def __cal_details(self):
        name = self.filename
        yaml_info = self.__yaml_info()
        atn0, atn1, atn2 = '0_00', '0_50', '1_20'
        attenuation = atn0
        if atn1 in name:
            attenuation = atn1
        elif atn2 in name:
            attenuation = atn2
        else:
            print("Incorrect Attenuation Values")
        file_name = "D{} F{}".format(yaml_info["imaging depth"], yaml_info["focal depth"])
        return file_name, attenuation

    def cal_phantom_files(self):
        self.__cal_raw()
        self.__cal_tgc()
        self.__cal_yaml()

    # Copies calibration files captured directly from the calibration phantom. Searches for the strings found in the
    # list called search. If a files contains one of these strings, it is copied and labeled with the calibration
    # information The variable search must be a list even if it is size one
    def __cal_phantom_copy(self, search):
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
        self.__cal_phantom_copy(["rf.raw", "env.raw"])

    # Copy yml files and renames them to match the calibration file with depth, focus, and attenuation values
    def __cal_yaml(self):
        self.__cal_phantom_copy(["rf.yml", "env.yml"])

    # Copy tgc files and renames them to match the calibration file with depth, focus, and attenuation values
    def __cal_tgc(self):
        self.__cal_phantom_copy(["env.tgc"])

    # Creates a .CSV file for calibration purposes. Generates the filename based on the depth, focus, and
    # attenuation values of the scan. Attenuation is read from the file name. Ensure 0_54 or 1_30 is
    # included in the file name.
    def cal_csv(self):
        data = self.data
        start_frame = self.num_frames
        filename = self.__cal_details()[0] + ".csv"
        self.__save_csv(filename, data, start_frame)

    # Creates a CSV file with the depth and focus of the scan. If multiple scans are processed, it appends these
    # values to the bottom of the CSV.
    def __cal_val_csv(self):
        cal_folder = os.path.join(self.folder_path, self.cal_folder_name)
        self.create_folder(cal_folder)
        file_name = os.path.join(cal_folder, self.cal_csv_name + ".csv")
        self.__add_cal_line(file_name)

    # Adds a new line to a CSV file. If this is the first line added to the CSV, it creates headers.
    def __add_cal_line(self, file_name):
        if not os.path.exists(file_name):  # If this is the first line added, it also creates headers
            header_vals = ["Scan name", "Depth", "Focus", "Transmit Freq"]
            self.new_csv_line(file_name, header_vals, 'w')
            self.new_csv_line(file_name[:-4] + " Not Found.csv", header_vals, 'w')  # This folder might remain empty
        yaml_info = self.__yaml_info()
        depth, focus, freq = yaml_info["imaging depth"], yaml_info["focal depth"], yaml_info["transmit frequency"][0:-4]
        csv_cal_vals = [self.__remove_file_type(self.filename), self.__remove_mm(depth), self.__remove_mm(focus), freq]

        # One thread runs this lineat a time. Prevents writing to a file that is open by another program.
        self.locker(self.cal_lock, lambda: self.new_csv_line(file_name, csv_cal_vals))  # This runs self.new_csv_line

    # Adds a new row to the end of a CSV file. Appends by default. Mode can be changed for write, create, etc.
    # line_vals should be passed to this function as a list of values. A string will be split into characters
    @staticmethod
    def new_csv_line(file_name, line_vals, mode='a'):
        with open(file_name, mode, newline='') as csv_out:  # newline = '' is needed or you get spaces between lines
            cal_writer = csv.writer(csv_out)
            cal_writer.writerow(line_vals)
            csv_out.close()

    # Checks a lock passed to the function; runs function if it is acquired successfully
    @staticmethod
    def locker(lock, locked_function):
        lock.acquire()  # lock.acquire automatically waits here until the lock is available
        locked_function()  # This is the function which is run on only one thread at a time.
        lock.release()

    # Searches the calibration library to check if the data has already been captured
    def check_cal_lib(self, cal_lib_path, delta=1.0):
        depth = self.__remove_mm(self.__yaml_info()['imaging depth'])
        depth_lib = ls_dir(cal_lib_path)
        closest_value = []
        min_diff = float("inf")
        for lib_search in depth_lib:
            lib_search_depth = self.__remove_focus(lib_search)
            try:
                difference = abs(float(lib_search_depth) - float(depth))
            # Some values will not be numbers (e.g. column titles), calculating this difference will cause a ValueError
            except ValueError:
                continue  # Skips this loop because a non-number (such as a title) is being compared
            # Finds the closest calibration data that is within the threshold of less than delta (0.5 mm by default)
            if difference <= delta and difference < min_diff:
                # This IF statment finds the frequency of the calibration data currently being seached to ensure it
                # matches the frequency of the participant scan. The transmit frequency changes from 4.0 HMz to 2.5
                # MHz when the depth raises past 100mm and back to 2.5MHz at 190mm
                calibration_folder = os.path.join(cal_lib_path, lib_search)  # First find the cal folder
                attenuation_folder = os.path.join(calibration_folder, os.listdir(calibration_folder)[0])

                if self.freq_match(attenuation_folder) and self.focus_match(attenuation_folder):
                    min_diff = difference
                    closest_value = difference, lib_search_depth

        if not closest_value:  # If no calibration value within delta of the measured value, add it the of not found CSV
            csv_title = self.cal_csv_name + " Not Found"
            cal_folder = os.path.join(self.folder_path, self.cal_folder_name)
            file_name = os.path.join(cal_folder, csv_title + ".csv")
            self.__add_cal_line(file_name)
        else:
            self.__copy_cal_files(closest_value[1], cal_lib_path)

    # Copies calibration files. Ensures the proper organization of folders. Avoids copying duplicates.
    def __copy_cal_files(self, depth_val, cal_lib_path):
        # Adding "D" before depth avoids partial matches. EG 30.0 is part of 130.0, but D30.0 is not part of D130.0
        depth_string = "D" + str(depth_val)
        cal_folder = os.path.join(self.folder_path, self.cal_folder_name)
        copy_location = os.path.join(self.folder_path, cal_folder)
        self.create_folder(cal_folder)

        depth_path = os.path.join(copy_location, self.__remove_file_type(self.filename))
        if os.path.exists(depth_path):
            shutil.rmtree(depth_path)
        for folder in ls_dir(cal_lib_path):
            if depth_string in folder and not os.path.exists(depth_path):
                shutil.copytree(os.path.join(cal_lib_path, folder), depth_path)

    # Deletes old CSV files so new information can replace them.
    @staticmethod
    def csv_cleanup(scan_folder_path):
        cal_csv_name = "Ultrasound Depth and Focus"
        cal_folder = "Ultrasound Calibration Data"
        found_cal_files = os.path.join(scan_folder_path, cal_folder, cal_csv_name + ".csv")
        missing_cal_files = os.path.join(scan_folder_path, cal_folder, cal_csv_name + " Not Found.csv")
        CData.remove_file(found_cal_files)
        CData.remove_file(missing_cal_files)

    # Removes an affix of length "suffix_len" from the end of a filename. EG __remove_affix("text.csv", 4) -> "text"
    # Also remove any whitespace at the start and end of the file name to prevent issues with folder naming
    @staticmethod
    def __remove_file_type(file_name):
        return '.'.join(file_name.split('.')[0:-1]).strip()

    # Removes " mm" (including the space) from the end of a file name. EG "55.55 mm" -> "55.55"
    @staticmethod
    def __remove_mm(measurement):
        return measurement[0:-3]

    # Given the format for Depth and Focus, D94.50 mm F47.23 mm, this prints only the Depth. EG returns 94.50
    @staticmethod
    def __remove_focus(depth_and_focus):
        return depth_and_focus[1:depth_and_focus.find('mm')].strip()

    # Creates a new directory only if it didn't exist before. Prevents duplicates and errors.
    @staticmethod
    def create_folder(folder_path):
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

    # Removes a file if it exists. Prevents errors if files do not exist in the first place.
    @staticmethod
    def remove_file(file_path):
        if os.path.isfile(file_path):
            os.remove(file_path)

    # This function doesn't work very well. It is not recommended.
    # Saves the data for the given frame into a csv file. This stores a B-Mode image that is distored.
    def __save_csv(self, file_name, data, frame):
        if os.path.isfile(os.path.join(self.folder_name, file_name)):
            print(".CSV RF data file already exists")
        else:
            scan_info_header = self.__yaml_header()
            np.savetxt(os.path.join(self.folder_name, file_name),
                       np.transpose(data[:, :, frame]), delimiter=",", header=scan_info_header)

    def transmit_freq(self):
        return self.__yaml_info()["transmit frequency"]

    def focal_depth(self):
        return self.__yaml_info()["focal depth"]

    def imaging_depth(self):
        return self.__yaml_info()['imaging depth']

    # Compares the transmit frequency of the RF data witht the transmit frequency of the calibration data.
    def freq_match(self, attenuation_folder):
        calibration_freq = self.__yaml_info(attenuation_folder)["transmit frequency"]  # Freq of the cal data
        if self.transmit_freq() == calibration_freq:  # Only record depth if frequency is correct
            return True
        else:
            print(f"Freq: RF = {self.transmit_freq()}, Cal = {calibration_freq}")
            return False

    # Compares the focus value of the RF data with the focus value of the calibration data. This should only really
    # return Flase if the default settings were changed on the Clarius. Focus should be 1/2 of the depth by default.
    def focus_match(self, attenuation_folder):
        tolerance_factor = 0.05  # Focus and depth values are rounded so this allows for some wiggle room
        cal_focus = self.__yaml_info(attenuation_folder)["focal depth"]
        if abs(float(self.__remove_mm(self.focal_depth())) / float(self.__remove_mm(cal_focus)) - 1) < tolerance_factor:
            return True
        else:
            print(f"Focus: RF = {self.focal_depth()}, Cal = {cal_focus}")
            return False
