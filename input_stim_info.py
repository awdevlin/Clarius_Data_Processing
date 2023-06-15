import os
import tkinter as tk
from tkinter import filedialog


# Class to create a GUI used to input patient data
class participant_Data:
    def __init__(self):
        self.stim_info = {}
        self.__define_input_box()
        self.__create_fields()
        self.window.mainloop()

    # Shape, size, and title of the window
    def __define_input_box(self):
        self.window = tk.Tk()
        self.window.title("STIMULUS Participant Info")
        self.window.geometry("")  # This should make the window the smallest size containing all of the elements

    # Creates entry regions for each data point and their labels
    def __create_fields(self):
        row_space = 2

        # Browse button to make it easier to enter the folder path. This deletes the scan_folder_path label
        browse_button_row = 0
        # self.browse_button = tk.Button(self.window, text="Browse for Folder Location", bg="black", fg="white",
        #                                command=self.__browse_files)
        # self.browse_button.grid(column=0, row=browse_button_row, pady=10, )

        # self.scan_folder_path = self.__label_and_entry("This gets deleted anyways", scan_folder_path_row,
        #                                                os.path.expanduser("~")
        #                                                )
        scan_folder_path_row = browse_button_row + 1
        self.scan_folder_path = InfoFields(self.window, scan_folder_path_row, 'Browse for Folder Location', os.path.expanduser("~"))
        self.scan_folder_path.create_button(self.__browse_files)
        self.scan_folder_path.create_entry()

        # site_loc_row = scan_folder_path_row + row_space
        # self.site_num = self.__label_and_entry("Enter Site Number: ", site_loc_row, "05")

        self.site_num = InfoFields(self.window, self.scan_folder_path.next_row(), "Enter Site Number: ", "05")
        self.site_num.create_label()
        self.site_num.create_entry()

        # mat_id_row = site_loc_row + row_space
        # self.mat_id = self.__label_and_entry("Maternal ID: ", mat_id_row, "STIM001")

        self.mat_id = InfoFields(self.window, self.site_num.next_row(), "Maternal ID: ", "STIM001")
        self.mat_id.create_label()
        self.mat_id.create_entry()

        # gest_age_row = mat_id_row + row_space
        # self.gest_age = self.__label_and_entry("Gestational Age (Weeks.Days): ", gest_age_row, "WW.D")

        self.gest_age = InfoFields(self.window, self.mat_id.next_row(), "Gestational Age (Weeks.Days): ", "WW.D")
        self.gest_age.create_label()
        self.gest_age.create_entry()

        # fet_num_row = gest_age_row + row_space
        # self.fet_num = self.__label_and_entry("Fetal Number: ", fet_num_row, "1")

        self.fet_num = InfoFields(self.window, self.gest_age.next_row(), "Fetal Number: ", "1")
        self.fet_num.create_label()
        self.fet_num.create_entry()

        # image_num_row = fet_num_row + row_space
        # self.im_num = self.__label_and_entry("Image Number: ", image_num_row, "1")

        self.im_num = InfoFields(self.window, self.fet_num.next_row(), "Image Number: ", "1")
        self.im_num.create_label()
        self.im_num.create_entry()

        radio_row = self.im_num.next_row()
        self.calibration_cb(radio_row)

        button_row = radio_row + row_space
        self.record_button = tk.Button(self.window, text="Enter Participant Info", bg="black", fg="white",
                                       command=self.__read_data)
        self.record_button.grid(column=0, row=button_row, pady=10)

    # Creates a checkbox that will allow the user to choose whether to pull calibration data from the library
    def calibration_cb(self, row, col=0):
        self.phantom_var = tk.IntVar()
        cb = tk.Checkbutton(self.window, text="Search Calibration Library", variable=self.phantom_var, offvalue=0,
                            onvalue=1)
        cb.grid(column=col, row=row)
        cb.select()

    # Allows for browsing folders. This can make it much easier to find the folder of interest
    def __browse_files(self):
        desktop_path = os.path.expanduser("~")
        self.scan_folder_path.entry.insert(0, filedialog.askdirectory(initialdir=desktop_path))
        self.scan_folder_path.entry.config(fg="black")

    # # Reads the entry from the label-entry pair that I use in this class
    # @staticmethod
    # def __get_entry(tk_pair):
    #     return tk_pair[1].get()

    # Reads all data entered into the data fields and return it to the function opening this GUI. It is designed to be
    # used at the press of a button .This function also closes the GUI.
    def __read_data(self):
        self.stim_info["scan_folder_path"] = self.scan_folder_path.get_entry()
        self.stim_info["project_site"] = self.site_num.get_entry()
        self.stim_info["maternal_id"] = self.mat_id.get_entry().upper()
        self.stim_info["gestational_age"] = self.gest_age.get_entry()
        self.stim_info["fetal_num"] = self.fet_num.get_entry()
        self.stim_info["image_num"] = self.im_num.get_entry()
        self.stim_info["cal_lib_search"] = self.phantom_var.get()
        self.stim_info["cal_lib_path"] = ""
        self.window.destroy()


class InfoFields:
    def __init__(self, window, row, label_text='', default_entry='', label_col=0, entry_col=0):
        self.stim_info = {}
        self.window = window
        self.row = row
        self.row_increment = 0
        self.label_text = label_text
        self.default_entry = default_entry
        self.label_col = label_col
        self.entry_col = entry_col
        self.label = tk.Label()
        self.entry = tk.Entry()

    def create_label(self):
        self.label = tk.Label(self.window, text=self.label_text)
        self.label.grid(column=self.label_col, row=self.row + self.row_increment, pady=5)
        self.row_increment += 1

    def create_entry(self):
        self.entry = tk.Entry(self.window, width=50, justify="center", borderwidth=3)
        self.entry.grid(column=self.entry_col, row=self.row + self.row_increment, padx=15)
        self.entry.insert(0, self.default_entry)
        self.entry.config(fg="grey")  # Default text starts greyed out
        # Bind passes the event tha triggered it so lambda e takes that event even though it's not used
        self.entry.bind("<FocusIn>", lambda e: self.__delete_text(self.entry))
        self.row_increment += 1

    def create_button(self, command):
        self.button = tk.Button(self.window, text=self.label_text, bg="black", fg="white",
                                command=command)
        self.button.grid(column=0, row=self.row + self.row_increment, pady=10, )
        self.row_increment += 1

    def next_row(self):
        return self.row + self.row_increment

    # Reads the entry from the label-entry pair that I use in this class
    def get_entry(self):
        return self.entry.get()

    # Use lambda function to delete text when first clicking on a box with grey template text. This delete happens once.
    # EG. event.bind("<FocusIn>", lambda e: self.__delete_text(event))
    # the 'e' in lambda e is required because bind() passes the event that triggers it.
    @staticmethod
    def __delete_text(entry):
        entry.delete(0, "end")
        entry.config(fg="black")
        entry.unbind("<FocusIn>")
