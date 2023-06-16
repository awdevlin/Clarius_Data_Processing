import os
import tkinter as tk
from tkinter import filedialog


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
        self.window.title("STIMULUS Participant Info")
        self.window.geometry("")  # This should make the window the smallest size containing all the elements

    # Creates entry regions for each data point and their labels
    def __create_fields(self):
        self.scan_folder_path = InfoFields(self.window, 0)
        self.scan_folder_path.create_button('Browse for Scan Folder', lambda: self.__browse_files(self.scan_folder_path))
        self.scan_folder_path.create_entry(os.path.expanduser("~"))

        self.site_num = InfoFields(self.window, self.scan_folder_path.next_row())
        self.site_num.create_label("Enter Site Number: ")
        self.site_num.create_entry("05")

        self.mat_id = InfoFields(self.window, self.site_num.next_row())
        self.mat_id.create_label("Maternal ID: ")
        self.mat_id.create_entry("STIM001")

        self.gest_age = InfoFields(self.window, self.mat_id.next_row())
        self.gest_age.create_label("Gestational Age: ")
        self.gest_age.create_entry("WW.D")

        self.fet_num = InfoFields(self.window, self.gest_age.next_row())
        self.fet_num.create_label("Fetal Number: ")
        self.fet_num.create_entry("1")

        self.im_num = InfoFields(self.window, self.fet_num.next_row())
        self.im_num.create_label("Image Number: ")
        self.im_num.create_entry("1")

        self.bmode_cb = InfoFields(self.window, self.im_num.next_row())
        self.bmode_cb.create_check_box("B-Mode Sample", False, "", 1)

        self.calibration_cb = InfoFields(self.window, self.im_num.next_row())
        self.calibration_cb.create_check_box("Search Calibration Library", False,
                                             lambda: self.__grey_out(self.calibration_cb, self.cal_lib_browse))

        self.cal_lib_browse = InfoFields(self.window, self.calibration_cb.next_row())
        self.cal_lib_browse.create_button("Browse for Calibration Library",
                                          lambda: self.__browse_files(self.cal_lib_browse))
        self.cal_lib_browse.create_entry(os.path.expanduser("~"))

        self.record_button = InfoFields(self.window, self.cal_lib_browse.next_row())
        self.record_button.create_button("Record Participant Info", self.__read_data)

    # Allows for browsing folders. This can make it much easier to find the folder of interest
    def __browse_files(self, info_fields):
        desktop_path = os.path.expanduser("~")
        info_fields.entry.delete(0, "end")
        info_fields.entry.insert(0, filedialog.askdirectory(initialdir=desktop_path))
        info_fields.entry.config(fg="black")

    @staticmethod
    def __grey_out(field, target, event=None):
        if field.get_cb():
            target.button.config(bg="black", fg="white", state="normal")
            target.entry.config(bg="white", fg="black", state="normal")
        else:
            target.button.config(bg="grey", fg="grey", state="disabled")
            target.entry.config(bg="grey", fg="grey", state="disabled")

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
        if self.calibration_cb.get_cb():
            self.stim_info["cal_lib_path"] = self.cal_lib_browse.get_entry()
        else:
            self.stim_info["cal_lib_path"] = ''
        if self.bmode_cb.get_cb():
            self.stim_info["b-mode_plot"] = 1
            print("b-mode_plot checked")
        else:
            self.stim_info["b-mode_plot"] = 0
            print("b-mode_plot not checked")
        self.window.destroy()


class InfoFields:
    def __init__(self, window, row):
        self.window = window
        self.row = row
        self.row_increment = 0
        self.entry = tk.Entry
        self.label = tk.Label
        self.button = tk.Button
        self.cb_var = tk.IntVar()

    def create_label(self, text, col=0):
        self.label = tk.Label(self.window, text=text)
        self.label.grid(column=col, row=self.row + self.row_increment, pady=5, sticky="w", padx=15)
        self.row_increment += 1

    def create_entry(self, text="", col=0, span=2):
        self.entry = tk.Entry(self.window, width=65, justify="center", borderwidth=3)
        self.entry.grid(column=col, row=self.row + self.row_increment, columnspan=span, padx=15, sticky="e")
        self.entry.insert(0, text)
        self.entry.config(fg="grey")  # Default text starts greyed out
        # Bind passes the event tha triggered it so lambda e takes that event even though it's not used
        self.entry.bind("<FocusIn>", lambda e: self.__delete_text(self.entry))
        self.row_increment += 1

    def create_button(self, text, command, col=0, span=2):
        self.button = tk.Button(self.window, text=text, bg="black", fg="white",
                                command=command, width=25)
        self.button.grid(column=col, row=self.row + self.row_increment, pady=10, columnspan=span, sticky="w", padx=15)
        self.row_increment += 1

    # Creates a checkbox that will allow the user to choose whether to pull calibration data from the library
    def create_check_box(self, text, selected, command, col=0):
        self.cb_var = tk.IntVar()
        cb = tk.Checkbutton(self.window, text=text, variable=self.cb_var, command=command)
        cb.grid(column=col, row=self.row + self.row_increment, pady=(15, 0))
        if selected:
            cb.select()
        if col == 0:
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
