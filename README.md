[December 2025 important update!  There was a bug in release 2.0 that would mess up the data in the sqlite database when a vendor is missing some data that it should have sent.
The fix is in the current 2.1 release. This bug did NOT impact the tsv files at all - none of those need to be re-created. However, if you use the counterdata.db file, I strongly
recommend that you delete your old counterdata.db file and run all of your reports again fully to make sure you have correct data there.
If you would like to just download the changed files instead of the whole src package, you can simply copy these two files into your local src folder: fetch_json.py and process_item_details.py .  
I also updated the order of packages in requirements.txt to make it easier for windows users but if you are already installed and running, that change will not impact you at all. - Melissa Belvadi]


# C5.1_Harvester

Python code to harvest COUNTER 5.1 Metrics usage data reports using the COUNTER API, generate the TSV files, and store the data in an sqlite database for further analysis

[Documentation](docs/README.md) - written for librarians

**Melissa Belvadi** wrote the backend and the 1.0 version that only offered a command-line interface. She is a librarian at the University of Prince Edward Island and is the maintainer of this code. If anyone would be interested in getting involved, contact her at mbelvadi@upei.ca

**Daniel Odoom**, a core contributor, wrote the GUI using PyQt6 and integrated the backend code to make version 2.0, released in October, 2025. He is a Computer Science student actively seeking new opportunities, and can be reached for professional inquiries at  dkodoom2002@gmail.com

For more information about COUNTER Metrics and the reports, see the [Education section of COUNTER's website](https://www.countermetrics.org/education/)


