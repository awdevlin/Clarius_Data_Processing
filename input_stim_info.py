import os
import tkinter as tk
from tkinter import *
from tkinter import filedialog


class participant_Data:
    def __init__(self):
        self.stim_info = {}
        self.__define_input_box()
        self.__create_fields()
        self.window.mainloop()

    def __define_input_box(self):
        self.window = tk.Tk()
        self.window.title("STIMULUS Participant Info")
        self.window.geometry("335x390")

    def __create_fields(self):
        row_space = 2
        scan_folder_path_row = 0
        self.scan_folder_path = self.__label_and_entry("Folder Location: ", scan_folder_path_row)

        # Browse button for easier folder path
        self.browse_button = tk.Button(self.window, text="Browse for Folder Location", bg="black", fg="white", command=self.__browse_files)
        self.browse_button.grid(column=0, row=scan_folder_path_row, pady=10)

        site_loc_row = scan_folder_path_row + row_space
        self.site_num = self.__label_and_entry("Enter Site Number: ", site_loc_row, "5")

        mat_id_row = site_loc_row + row_space
        self.mat_id = self.__label_and_entry("Maternal ID: ", mat_id_row, "STIM")

        gest_age_row = mat_id_row + row_space
        self.gest_age = self.__label_and_entry("Gestational Age (Weeks.Days): ", gest_age_row, "00.0")

        fet_num_row = gest_age_row + row_space
        self.fet_num = self.__label_and_entry("Fetal Number: ", fet_num_row, "1")

        image_num_row = fet_num_row + row_space
        self.im_num = self.__label_and_entry("Image Number: ", image_num_row, "1")

        radio_row = image_num_row + row_space
        self.calibration_cb(radio_row)

        button_row = radio_row + row_space
        self.record_button = tk.Button(self.window, text="Enter Participant Info", bg="black", fg="white", command=self.__read_data)
        self.record_button.grid(column=0, row=button_row, pady=10)

    def __label_and_entry(self, label_text, row, default_entry='', label_col=0, entry_col=0):
        label = tk.Label(self.window, text=label_text)
        label.grid(column=label_col, row=row, pady=5)
        entry = tk.Entry(self.window, width=50, justify="center")
        entry.grid(column=entry_col, row=row+1, padx=15)
        entry.insert(0, default_entry)
        return label, entry

    # Reads the data from the fields in the entry window
    def __read_data(self):
        self.stim_info["scan_folder_path"] = self.__get_entry(self.scan_folder_path)
        self.stim_info["project_site"] = self.__get_entry(self.site_num)
        self.stim_info["maternal_id"] = self.__get_entry(self.mat_id)
        self.stim_info["gestational_age"] = self.__get_entry(self.gest_age)
        self.stim_info["fetal_num"] = self.__get_entry(self.fet_num)
        self.stim_info["image_num"] = self.__get_entry(self.im_num)
        self.stim_info["cal_lib_search"] = self.phantom_var.get()
        self.window.destroy()

    @staticmethod
    def __get_entry(tk_pair):
        return tk_pair[1].get()

    def __browse_files(self):
        self.scan_folder_path[1].insert(0, tk.filedialog.askdirectory(initialdir="C:/"))

    def calibration_cb(self, row, col=0):
        self.phantom_var = IntVar()
        cb = tk.Checkbutton(self.window, text="Search Calibration Library", variable=self.phantom_var, offvalue=0, onvalue=1)
        cb.grid(column=col, row=row)
        cb.select()

    # Might use this function to create grayed out text for some entries
    def __delete_entry(self, _):
        self.delete(0, tk.END)
