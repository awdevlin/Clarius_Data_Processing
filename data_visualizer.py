from hzhu_clarius import *

# Data collected using Clarius Cast API

# Path to the file unzip_data.exe
lzop_path = r"C:\Users\mrave\OneDrive\Desktop\Clarius-raw-data-main\Clarius-raw-data-main"

# Path to the folder where data is stored
folder_path = r"C:\Users\mrave\OneDrive\Desktop\Phantom Data"

# Data folder name. Should be a zipped file with .tar format
# filename = "heart test 1.tar"

# Create a data handle for the processing and visualization of the data
# cdata = CData(folder_path=folder_path, filename=filename, lzop_path=lzop_path)

# cdata.csv_out(0)
# cdata.plot_rf(0,1500,30)

for scan_title in ls_file(folder_path):
    if '.tar' in scan_title:
        print(scan_title)
        cdata = CData(folder_path=folder_path, filename=scan_title, lzop_path=lzop_path)
        # print(cdata.num_frames)
        # cdata.csv_all_frames()
        cdata.csv_out(5)
