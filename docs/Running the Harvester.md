# Starting and Running the Harvester 2.0 with GUI Interface

After you've set up the current_config.py and providers.tsv to your needs, you simply run the program with this command line:
python3 main.py     (depending on your operating system, you might leave off the "3").

You may do that using a command line window or you may be able to set up a desktop icon to do that for you.
If you needed to create a "virtual environment" for the harvester so the dependency packages do not interfere with other python programs you use, you may want to create a desktop shortcut to a script that does all of those steps for you (change directory to where the program is installed, activate the virtual environment, then start the program).

The GUI allows you to set all of the relevant options:
- The start and end dates to request the data for.
--The start date default is set in the current_config.py file (which you can easily modify using the Settings button) so you can change it as fits your workflow. For instance, throughout 2025, you may want the start date to always default to January 2025, then in 2026, you may want your start date to always default to January 2026.
-- The end data always defaults to the month before the current one, a per the COUNTER standard that data is always provided in full months, so the latest possible data is always in the next month, eg January 2026 data will not be available until February 2026. Note further that providers have until 28 days into the new month so January 2026 data may be not available until February 28, 2026, although many providers release their data much sooner into the new month than that.
– You can easily override the defaults for any specific harvest run using the month and year boxes provided.

The harvester checks the date range available from each provider compared to your request and adjusts the range per provider to only include YYYY-MM that the provider supports (and warns you of any adjustments in the progress log and the error log).

- You can select any or all of the providers to include in this run using the checkboxes provided.
- You can select any or all of the report types to include in this run using the checkboxes provided.
- - The harvester will check your list of requested report types against what that provider's API server tells it are the supported report types and only request the supported ones.

When you press the Start button, it just runs until it is done. Depending on how many providers have required delays and retries, it could take a few minutes or even hours, as it processes each report request fully one at a time. It provides a "progress log" in a special window and will give special notice there for problems that you probably want to know about, especially if a provider/report won't have the data you asked for, e.g., unsupported report types, or data not available for that date range.

In addition to the progress log, which you can save to look through further later, there is also a more detailed errorlog.txt file, which is a plain text file.
The error log file is reset to empty after every run, so copy it to somewhere else before your next run it if you want to examine it. It will have more detailed data than the progess log, including exact API URL links for each report request, which may help you troubleshoot problems with individual providers. 

You can actually paste a COUNTER API URL directly into your favorite web browser to see if it works, and if there was a problem with it. If it returns anything other than a generic HTTP error, that response will be in json.  You can share that link with that provider's tech support or anyone else you have helping you. Just be aware that it contains all of your "credentials" (customer_id, requestor_id, and api_key) and some people consider parts of that to be like "passwords" so think carefully about where you share it.

These are the steps it goes through after you start a harvest run:
1. for each selected provider, run a COUNTER-defined API command to get the list of reports that provider supports (eg a journals-only platform won't support TR_B1 which is for books) and then limits the list to the ones you selected
2. fetch the json for each selected report and save it into its own json file
3. use that json to generate .tsv files just like you would have gotten interactively from the provider's own "institutional admin" website
4. use that data again to add it to an sqlite database to run more complex searches than you can do in an individual spreadsheet

You can stop the harvester while it is running, by using the STOP button. However, that will not undo whatever was saved to that point, including json and tsv files, and data saved in the sqlite database.

