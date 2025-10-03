# Configuration options

While you can change whatever you like in your own copy of the source code, a few specific options are made easy for you to change in the current_config.py file. You may well choose to leave all of these in their default values.

Those options are, with their default settings:

- **sqlite_filename** = 'counterdata.db'
- **data_table** = 'usage_data'
- **info_log_file** = 'info_log.txt'
- **json_dir** = 'json_folder'
- **tsv_dir** = 'tsv_folder'
- **providers_file** = 'providers.tsv'
- **save_empty_report** = True
- **always_include_header_metric_types** = True
- **default_begin** = '2025-01'

There is also a default_config.py which store the harvester's original values in case you want to revert to those. We strongly recommend you not edit that file.

We recommend that you do not change any of the file or folder names unless you have a specific reason, such as wanting to deliberately create a new file/folder structure leaving the old one untouched. Changing these settings after you have run the harvester at least once does NOT rename existing files/folders but just leaves them alone and creates new ones using your new names.

Do ***not*** try to completely change the path outside of the main program folder where the harvester python code is saved. The 
harvester will expect those to be subfolders directly below the folder where the python code is saved..

The name of "data_table" is just the actual table name in the sqlite database.

## "always_include_header_metric_types"

The COUNTER standard is to not include the list of metric types if the list would be the default list.  This variable gives you the option to always include them anyway so you can immediately see exactly what metric types are included. To follow the COUNTER standard, change this to **False**.

## "save_empty_report"

If this is set to True, the Harvester will make a file for every report_header it gets even if there were no report_items. 
This most commonly occurs when you have an error ("exception") like "3030: No usage for requested dates".
When it does create these "empty" reports (they have the header but no table of data because none was provided), it puts the word "empty" at the end of the filename, eg. "AAAS_DR_D2_2025-01-2025-03_2025_04_30_empty.tsv"
The reason you might want this is so that you can see that the attempt was made but there just was no data, rather than wondering why some tsv files seem to be "missing". But it's your choice.

## providers.tsv
Unless you have a specific need to swap out different lists of providers between harvest runs, we strongly recommend that you leave this alone and make sure that file has all of your providers and their settings. The GUI lets you choose which providers to harvest each time you run one.
