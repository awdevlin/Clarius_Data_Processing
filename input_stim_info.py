import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
# from data_processing import tar_processing
from clarius import *


# Class to create a GUI used to input patient data
class participant_Data:
    def __init__(self):
        self.stim_info = {}
        self.__define_input_box()
        self.__create_fields()
        self.__grey_out(self.calibration_cb, self.cal_lib_browse)
        self.window.mainloop()

    # Shape, size, and title of the window
    def __define_input_box(self):
        self.window = tk.Tk()
        self.window.title("STIMULUS Participant Data")
        self.window.geometry("")  # This makes the window the smallest size that still contains all the elements

    # Creates entry regions for each data point and their labels
    def __create_fields(self):
        self.scan_folder_path = InfoFields(self.window, 0)
        self.scan_folder_path.create_button('Browse to Participant Folder',
                                            lambda: self.__browse_files(self.scan_folder_path))
        self.scan_folder_path.create_entry(os.path.expanduser("~"))

        self.site_num = InfoFields(self.window, self.scan_folder_path.next_row())
        self.site_num.create_label("Enter Site Number: ")
        self.site_num.create_entry("05")

        self.mat_id = InfoFields(self.window, self.site_num.next_row())
        self.mat_id.create_label("Maternal ID: ")
        self.mat_id.create_entry("STIM000")

        self.gest_age = InfoFields(self.window, self.mat_id.next_row())
        self.gest_age.create_label("Gestational Age: ")
        self.gest_age.create_entry("WW.D")

        self.fet_num = InfoFields(self.window, self.gest_age.next_row())
        self.fet_num.create_label("Fetal Number: ")
        self.fet_num.create_entry("1")

        self.im_num = InfoFields(self.window, self.fet_num.next_row())
        self.im_num.create_label("Image Number: ")
        self.im_num.create_entry("1")

        cb_col = 0
        self.calibration_cb = InfoFields(self.window, self.im_num.next_row())
        self.calibration_cb.create_check_box("Search Calibration Library", False,
                                             lambda: self.__grey_out(self.calibration_cb, self.cal_lib_browse), cb_col)

        self.collecting_cal_data = InfoFields(self.window, self.im_num.next_row())
        self.collecting_cal_data.create_check_box("Collecting Calibration Data", False, "", cb_col + 1)

        self.bmode_cb = InfoFields(self.window, self.im_num.next_row())
        self.bmode_cb.create_check_box("B-Mode Sample", False, "", cb_col + 2)

        self.cal_lib_browse = InfoFields(self.window, self.calibration_cb.next_row())
        self.cal_lib_browse.create_button("Browse for Calibration Library",
                                          lambda: self.__browse_files(self.cal_lib_browse))
        self.cal_lib_browse.create_entry(os.path.expanduser("~"))

        self.record_button = InfoFields(self.window, self.cal_lib_browse.next_row())
        self.record_button.create_button("Process Participant Data", self.__read_data)
        self.record_button.row -= 1
        self.record_button.create_label("", 2)

    # Allows for browsing folders. This can make it much easier to find the folder of interest
    @staticmethod
    def __browse_files(info_fields):
        desktop_path = os.path.expanduser("~")
        info_fields.entry.delete(0, "end")
        info_fields.entry.insert(0, filedialog.askdirectory(initialdir=desktop_path))
        info_fields.entry.config(fg="black")
        info_fields.entry.unbind("<FocusIn>")

    @staticmethod
    def __grey_out(check_button, target):
        if check_button.get_cb():
            target.button.config(bg="black", fg="white", state="normal")
            target.entry.config(bg="white", state="normal")
        else:
            target.button.config(bg="grey", fg="grey", state="disabled")
            target.entry.config(bg="grey", state="disabled")

    # Reads all data entered into the data fields and return it to the function opening this GUI. It is designed to be
    # used at the press of a button .This function also closes the GUI.
    def __read_data(self):
        self.stim_info["scan_folder_path"] = self.scan_folder_path.get_entry()
        self.stim_info["project_site"] = self.site_num.get_entry()
        self.stim_info["maternal_id"] = self.mat_id.get_entry().upper()
        self.stim_info["gestational_age"] = self.gest_age.get_entry()
        self.stim_info["fetal_num"] = self.fet_num.get_entry()
        self.stim_info["image_num"] = self.im_num.get_entry()
        self.stim_info["cal_lib_search"] = self.calibration_cb.get_cb()
        self.stim_info["cal_lib_path"] = self.__get_cal_path()
        self.stim_info["b-mode_plot"] = self.bmode_cb.get_cb()
        self.stim_info["collecting_cal_data"] = self.collecting_cal_data.get_cb()
        self.stim_info["raw_or_rend"] = "raw"  # Clarius only stores raw images for now, this may change later

        # close the tkinter window if participant information was entered completely. Else send warning message
        if self.__check_stim_info():
            self.update_progress('Running')
            tar_processing(self.stim_info)
            self.update_progress('Done!')
        else:
            messagebox.showwarning(title='Data Entry Warning', message='All Information Fields Must Be Filled')

    def __get_cal_path(self):
        if self.calibration_cb.get_cb():
            return self.cal_lib_browse.get_entry()
        return ''

    # Check if any values are left blank in the GUI when recording participant data
    def __check_stim_info(self):
        for field in self.stim_info:
            # Catches a blank entry in stim_info. If that entry is the calibration library folder_path and the user
            # is not looking for calibration data, that is allowed to be blank
            if self.stim_info[field] == '' and not (field == "cal_lib_path" and not self.calibration_cb.get_cb()):
                return False
        return True

    def update_progress(self, text):
        self.record_button.label.config(text=text)
        self.record_button.label.update()


# This class uses Tkinter to create a GUI elements that share information. For example, you can create a
# Label and an Entry field from the same information. Their functions will be linked and creating them is streamlined
# after their information has been initially entered
class InfoFields:
    def __init__(self, window, row):
        self.window = window
        self.row = row
        self.row_increment = 0
        self.entry = tk.Entry
        self.label = tk.Label
        self.button = tk.Button
        self.cb_var = tk.IntVar()
        self.pady = 15
        self.padx = 15

    def create_label(self, text, col=0):
        self.label = tk.Label(self.window, text=text)
        self.label.grid(column=col, row=self.row + self.row_increment, pady=(self.pady, 0), sticky="w", padx=self.padx)
        self.row_increment += 1

    def create_entry(self, text="", col=0, col_span=3):
        self.entry = tk.Entry(self.window, width=75, justify="center", borderwidth=3)
        self.entry.grid(column=col, row=self.row + self.row_increment, columnspan=col_span, padx=self.padx, sticky="w")
        self.entry.insert(0, text)
        self.entry.config(fg="grey")  # Default text starts greyed out

        # Bind() passes the event that triggered it to the lambda function as the parameter e; it's not used for
        # anything, but it must be handled
        self.entry.bind("<FocusIn>", lambda e: self.__delete_text(self.entry))
        self.entry.bind("<FocusOut>", lambda e: self.__focusout_replace(self.entry, text))
        self.row_increment += 1

    def create_button(self, text, command, col=0, span=2):
        self.button = tk.Button(self.window, text=text, bg="black", fg="white", command=command, width=25)
        self.button.grid(column=col, row=self.row + self.row_increment, pady=(self.pady, 10), columnspan=span,
                         sticky="w", padx=self.padx)
        self.row_increment += 1

    # Creates a checkbox that will allow the user to choose whether to pull calibration data from the library
    def create_check_box(self, text, selected, command, col=0):
        self.cb_var = tk.IntVar()
        cb = tk.Checkbutton(self.window, text=text, variable=self.cb_var, command=command)
        cb.grid(column=col, row=self.row + self.row_increment, pady=(self.pady, 0))
        if selected:
            cb.select()
        self.row_increment += 1

    # Returns the next row after that last row used by this class.
    def next_row(self):
        return self.row + self.row_increment

    # Reads the value from an entry used in this class.
    def get_entry(self):
        return self.entry.get()

    def get_cb(self):
        return self.cb_var.get()

    # Use lambda function to delete text when first clicking on a box with grey template text. This delete happens once.
    # EG. event.bind("<FocusIn>", lambda e: self.__delete_text(event))
    # the 'e' in lambda e is required because bind() passes the event that triggers it.
    @staticmethod
    def __delete_text(entry):
        entry.delete(0, "end")
        entry.config(fg="black")
        entry.unbind("<FocusIn>")

    # If no information is found in the Entry, fill it with the default text
    def __focusout_replace(self, entry, old_text):
        if entry.get() == "":
            entry.insert(0, old_text)
            entry.config(fg="grey")
            entry.bind("<FocusIn>", lambda e: self.__delete_text(entry))


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
        # pData.update_progress(round((scan_count + 1) / len(ls_file(scan_folder_path)) * 100, 0), '%')
        scan_count += 1


participant_Data()
