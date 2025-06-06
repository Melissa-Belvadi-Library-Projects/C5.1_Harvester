While you can change whatever you like in your own copy of the source code, a few specific options are made easy for you to change in the sushiconfig.py file.
Those options are:

- sqlite_filename = 'counterdata.db'
- data_table = 'usage_data'
- error_log_file = 'errorlog.txt'
- json_dir = 'json_folder'
- tsv_dir = 'tsv_folder'
- providers_file = 'providers.tsv'
- save_empty_report = True
- always_include_header_metric_types = True
- default_begin = '2025-01'

Most of these are self-explanatory.
The "dirs" can be renamed but don't try to completely change the path outside of the main program folder as parts of the 
Harvester will expect those to be subfolders directly below the main Harvester folder.

The name of "data_table" is just the actual table name in the sqlite database.

Regarding **"always_include_header_metric_types"**:
the COUNTER standard is to not include the list of metric types if the list would be the default list.  This variable gives you the option to always include them anyway so you can immediately see exactly what metric types are included
(True), or follow the standard (False)

Regarding **"save_empty_report"**:If this is set to True, the Harvester will make a file for every report_header it gets even if there were no report_items. 
This most commonly occurs when you have an error ("exception") like "3030: No usage for requested dates".
When it does create these "empty" reports (they have the header but no table of data), it puts the word "empty" at the end of the filename, eg. "AAAS_DR_D2_2025-01-2025-03_2025_04_30_empty.tsv"
The reason you might want this is so that you can see that the attempt was made but there just was no data, rather than wondering why some tsv files seem to be "missing". But it's your choice.

Regarding **providers.tsv** - best practice advice:
If there are times you want to run just a specific provider and not your usual whole list, you have two choices on how to do that. The first is to edit the providers_file in sushiconfig to reference a different file that has only
the one provider. Or you could leave that setting alone and do some file copying/editing, eg rename providers.tsv to all_providers.tsv then rename one_provider.tsv to providers.tsv. Either way you'll need to remember to undo the change
when you want to leave the Harvester ready to harvest the entire list of providers next time.
