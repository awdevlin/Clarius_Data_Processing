from hzhu_clarius import *

# Data collected using Clarius Cast API

# Path to the file unzip_data.exe (if relative path doesn't work, use absolute)
# lzop_path = r"..\Clarius-raw-data"

lzop_path = os.getcwd()

# Path to the folder where data is stored
folder_path = r"C:\Users\mrave\OneDrive\Desktop\Clarius Data\23-03-29 Time Test"

for scan_title in ls_file(folder_path):
    if '.tar' in scan_title:
        print(scan_title)

        # Create a data handle for the processing and visualization of the data
        cdata = CData(folder_path=folder_path, filename=scan_title, lzop_path=lzop_path)

        # cdata.csv_all_frames()
        cdata.csv_out(5)
