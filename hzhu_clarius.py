import shutil
import os
import subprocess
import numpy as np
from scipy.signal import hilbert
import matplotlib.pyplot as plt
import sys
import rdataread as rd
import yaml

from hzhu_gen import *


class CData:
    def __init__(self, folder_path, filename, lzop_path):
        self.folder_path = folder_path
        self.filename = filename
        self.lzop_path = lzop_path
        self.folder_name = os.path.join(self.folder_path, *filename.split('.')[0:-1])
        shutil.unpack_archive(os.path.join(self.folder_path, filename), self.folder_name)
        self.files = ls_file(self.folder_name)

        for item in self.files:
            if '.raw.lzo' in item:
                out = subprocess.run(
                    '\"%s\\unzip_data.exe\" -d \"%s\"' % (self.lzop_path, os.path.join(self.folder_name, item)),
                    shell=True)
                os.remove(os.path.join(self.folder_name, item))
        self.files = ls_file(self.folder_name)
        try:
            self.num_frames = self.get_rf()[0]['frames']
        except Exception as e:
            print(e)
            self.num_frames = 1

    def get_rf(self):
        for item in self.files:
            if 'rf.raw' in item:
                return rd.read_rf(os.path.join(self.folder_name, item))
        return None

    def plot_rf(self, start=0, stop=float('inf'), step=1):
        hdr, timestamps, data = self.get_rf()
        stop = min(hdr['frames'], stop)

        # convert to B
        bdata = np.zeros((hdr['lines'], hdr['samples'], hdr['frames']), dtype='float')
        for frame in range(start, stop, step):
            bdata[:, :, frame] = 20 * np.log10(np.abs(1 + hilbert(data[:, :, frame])))

        # display images
        for frame in range(start, stop, step):
            plt.figure(figsize=(10, 5))
            plt.subplot(1, 2, 1)
            plt.imshow(np.transpose(data[:, :, frame]), cmap=plt.cm.gray, aspect='auto', vmin=-1000, vmax=1000)
            plt.title('RF frame ' + str(frame))
            plt.subplot(1, 2, 2)
            plt.imshow(np.transpose(bdata[:, :, frame]), cmap=plt.cm.gray, aspect='auto', vmin=15, vmax=70)
            plt.title('sample B frame ' + str(frame))
            plt.show()

    def csv_out(self, frame):
        hdr, timestamps, data = self.get_rf()
        name = self.filename[0:len(self.filename) - 4]
        start_frame = self.num_frames - frame
        if start_frame < 0:
            start_frame = 0
            frame = self.num_frames
        for f in range(frame):
            file_name = name + " frame {}.csv".format(start_frame + f)
            if os.path.isfile(self.folder_name + "/" + file_name):
                print(".CSV RF data file already exists")
            else:
                scan_info_header = self.__yaml_header()
                np.savetxt(self.folder_name + "/" + file_name,
                           np.transpose(data[:, :, f]), delimiter=",", header=scan_info_header)
                print(round((f + 1) / frame * 100, 0), '%')

    def csv_all_frames(self):
        self.csv_out(self.num_frames)

    # Describes the parameters of the scan. Creates a header for the CSV file using the yaml file information. The
    # output is separated by commas to work with .CSV format
    def __yaml_header(self):
        yaml_info = self.__yaml_info()
        imaging_depth = yaml_info["imaging depth"]
        focal_depth = yaml_info["focal depth"]
        tgc = yaml_info["tgc"]
        full_header = ",imaging depth," + imaging_depth + "," + "focal_depth," + focal_depth + "," + "tgc,"

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
        with open(folder_path + "/" + rf_yml_file_name) as file:
            yaml_info = yaml.safe_load(file)
        return yaml_info

    def calibration_csv(self):
        hdr, timestamps, data = self.get_rf()
        name = self.filename[0:len(self.filename) - 4]
        start_frame = self.num_frames
        yaml_info = self.__yaml_info()
        scan_info_header = self.__yaml_header()
        attenuation = '0_00'
        if '0_54' in name:
            attenuation = '0_54'
        elif '1_30' in name:
            attenuation = '1_30'
        file_name = "D{} F{} {}.csv".format(yaml_info["imaging depth"], yaml_info["focal depth"], attenuation)
        if os.path.isfile(self.folder_name + "/" + file_name):
            print(".CSV RF data file already exists")
        else:
            np.savetxt(self.folder_name + "/" + file_name,
                       np.transpose(data[:, :, start_frame - 1]), delimiter=",", header=scan_info_header)
