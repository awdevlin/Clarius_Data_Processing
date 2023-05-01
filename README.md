# Clarius-raw-data
Processing and visualizing raw data collected from Clarius probes

The raw data downloaded by using Clarius probes with Clarius Cast API comes individual zip files with binary image data (doubly compressed) and machine parameters. For the convenient reading and processing directly from the collected tar files, I created python codes to extract and transform the data into usable format, i.e., numpy array and python dict. This code is adopted from Clarius official repositories. This code works for Windows OS only.

To run the code, the following packages are needed with Python 3:
- Numpy
- Scipy
- Matplotlib

File “Visual.ipynb” shows an example of directing reading from a tar file. _CData_ is the class that handles tar file processing. It takes three arguments to initialize, which are _folder_path_ (the path to the intended tar file), _filename_ (the name for the tar file), and _lzop_path_ (the path to the unzip_data.exe file that extracts compressed data.

By calling _CData.get_rf()_, we can get all raw image data in the file. Examples of how to use the returned object from _CData.plot_rf()_ can be found in function _CData.plot_rf(...)_.

By calling _CData.plot_rf(start=0, stop=float('inf'), step)_, we can visualize the multi-frame data, starting from index _start_, ending with index _stop_ with increment step _step_.

___Note___: The unzip_data.exe file may be misidentified as a virus. Please white list the file if misidentified. 
