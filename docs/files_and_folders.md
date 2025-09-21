# What is saved where

This document explains what the harvester saves and where, for your COUNTER reports.

The harvester keeps everything in the folder where you installed it, including subfolders within that.

# JSON files:

The Harvester retrieves your COUNTER reports using the COUNTER API system, which sends the Harvester your data in a format called "json".
JSON is human readable, but only barely. If you want the technical details of the COUNTER json, see 
[The COUNTER json documentation](https://countermetrics.stoplight.io/docs/counter-sushi-api/au9uaf0yg84mo-counter-api)

The Harvester saves every json report it fetches in the folder specified in the current_config.py file; by default it is "json_folder".
Within json_folder will be subfolders for each provider, using the Provider_Name from your providers.tsv file.
It names the file with the following information separated by underscores:
**Provider-Name_Report-Type_Report-Begin-Date_Report-End-Date_Retrieved-Date.json**
Provider_Name comes from your providers.tsv. You specify the begin and end dates that you want included in the report when you run the Harvester.
The Retrieved-Date is the YYYY_MM_DD that you made this report.
The Report-Type is generated from the JSON reports themselves.
The Harvester uses the API to get a list of supported reports for each of your providers.
It will warn you if a provider also has custom reports, but it doesn't download them.
You will be able to select to retrieve all reports, or just some of them, in the harvester graphical interface.
You will get a warning in the progress log if your selections ask for a report that a provider does not support.

When your request includes any of the master reports (DR, PR, TR, IR), the harvester actually creates two reports, the original and an enhanced one that requests every possible data value, used to populate the database.
So in the json folders, you will see TR and TR_EX, PR and PR_EX, DR and DR_EX, and IR and IR_EX.
The EX ("extra") one is not a standard COUNTER report but a unique feature to this harvester.
The default reports don't include all possible data. For instance, the TR does not include the YOP (year of publication).
The COUNTER documentation at: https://cop5.projectcounter.org/en/5.1.0.1/04-reports/index.html lists the data (columns) 
that you will only get if you ask for it as the "C" rather than "M" "Column Elements". Those "C" data fields are the ones included in the "EX" requests and written to the database.

    Warning: some providers who have implemented the IR report are not providing parent elements properly or at all, even when specifically asked to include them. 
In those cases, only the IR_A1 has those and because they are not included in the sqlite database, you may be missing important info about the articles (like what journal they are in!), from the database.
Hopefully the providers who do this will become properly compliant. Since providers are required to provide the json data for two full years plus the current calendar year, if they get this fixed within that time, you will be able to re-request that data to get it into the database.


# TSV Files - the COUNTER reports:

After retrieving the json raw data, the harvester generates from that data a COUNTER-compliant "tsv" file that is 
intended to be opened in spreadsheet software like Excel and Google Sheets.
Those files are all saved in the subfolder "tsv_folder" (unless you changed the name in current_config.py), and just like the json_folder, it creates subfolders for each provider.
All tsv files in this folder are COUNTER standard files that are the same as what you would get manually downloading the reports from your provider's librarian admin/dashboard service with two exceptions:
- The _EX files are, as described above in the JSON explanation, specific to this harvester. They are the same as what you would get manually if you included all optional attributes, though
- If you chose "always_include_header_metric_types = True" in the current_config.py, the header will contain more information than the default COUNTER standard reports and views

# SQLITE Database:

> Important Update May 12, 2025 - major software improvements have invalidated the usage table format going forward, so if you used this harvester before that date, please start a fresh db file and re-run your report requests.

The harvester saves all of the data from all of the "_EX" json reports into an sqlite database.
The reason for the sqlite database is that it gives you the power to generate tsvs that combine data across all of your providers, instead of having to look one tsv at a time when you have, for instance, the same title across multiple platforms.

For more information about using the sqlite database, see the document "sqlite_database_info" in the harvester docs folder.
Note that the sqlite database can get very large over time depending on how many providers you have and especially how many support IR reports as IR_A1 and IR give a separate row for every usage at the article level rather than just journal title.

To reduce that size, the harvester will not save zero metric values in the database. For instance, if for a particular title in the title report of a specific provider, you had zero uses for every month except December, in the tsv file you will have zero values under each month-column except December, but in the sqlite database there will just be a December value, not the other months with zeros. If you ever have reason to question possible missing data, you can always look at the corresponding tsv file to confirm that the "missing" values are all zero.

Make sure you have at least a few Gigabytes of free space on the drive where you are putting all this.
Space is not a real concern for the json and tsv files, just the sqlite database.
It is a normal file so if you need to move it somewhere else on your computer, you can do that and start a new one; that will happen for you when you run the harvester and it doesn't see the counterdata.db file where current_config tells it to look. Because providers are required to keep 2 years plus current year available, you can always re-retrieve that much data when starting a new database.

# Deleting json and tsv files

You are free to do whatever you want with the files in the json_folder and tsv_folder tree. The harvester never looks back to use those or expects them to still be there. If they start to take up too much space, you are free to zip them, archive them elsewhere or anything else you want to do with them.

Because they (json and tsv) are stored with unique names for each provider, report_type, date range, AND run-date, you will start to get some significant build up over time. Depending on your computer's operating system and how often you run reports (eg yearly vs monthly for all providers), you may eventually approach some file/folder limitations of your system (eg how many files in a single folder).

If you do run exactly the same report on the same day, it will just overwrite the existing file with the updated version. But the next day, there will be a second report whose filename reflects the different date.

# The ERROR LOG File

Every time you run the harvester, it creates a new error log (empties the old one if it existed).
Most of this file is where important error messages are saved, but it also has a few lines tagged "INFO" that are 
not errors but give possibly useful information if there are problems with specific providers/reports. It also has "warnings". The most 
common warning is if you simply don't have any usage data for the time period you requested for any given report. Many of the errors and warnings are explained further in the [COUNTER Metrics Appendix D - Handling Errors and Exceptions](https://cop5.countermetrics.org/en/5.1.0.1/appendices/d-handling-errors-and-exceptions.html).

