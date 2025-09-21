# Configuration options

While you can change whatever you like in your own copy of the source code, a few specific options are made easy for you to change in the current_config.py file. 

Those options are, with their default settings:

- sqlite_filename = 'counterdata.db'
- data_table = 'usage_data'
- error_log_file = 'errorlog.txt'
- json_dir = 'json_folder'
- tsv_dir = 'tsv_folder'
- providers_file = 'providers.tsv'
- save_empty_report = True
- always_include_header_metric_types = True
- default_begin = '2025-01'

There is also a default_config.py which store the harvester's original values in case you want to revert to those.

We recommend that you do not change of the file or folder names unless you have a specific reason, such as wanting to deliberately create a new file/folder structure leaving the old one untouched. Changing these settings does NOT rename existing files/folders with the old name, just leaves them alone and creates new ones using your new names.

Do ***not*** try to completely change the path outside of the main program folder where the harvester python code is saved. The 
harvester will expect those to be subfolders directly below the folder where the python code is saved..

The name of "data_table" is just the actual table name in the sqlite database.

Regarding **"always_include_header_metric_types"**:
the COUNTER standard is to not include the list of metric types if the list would be the default list.  This variable gives you the option to always include them anyway so you can immediately see exactly what metric types are included
(True), or follow the COUNTER standard (False)

Regarding **"save_empty_report"**:If this is set to True, the Harvester will make a file for every report_header it gets even if there were no report_items. 
This most commonly occurs when you have an error ("exception") like "3030: No usage for requested dates".
When it does create these "empty" reports (they have the header but no table of data), it puts the word "empty" at the end of the filename, eg. "AAAS_DR_D2_2025-01-2025-03_2025_04_30_empty.tsv"
The reason you might want this is so that you can see that the attempt was made but there just was no data, rather than wondering why some tsv files seem to be "missing". But it's your choice.

Regarding **providers.tsv** - best practice advice:
Leave this alone and make sure that file has all of your providers and their settings. The GUI lets you choose which to harvest each time you "start" a harvest run.
