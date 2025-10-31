# Starting and Running the Harvester 2.0 with GUI Interface

These instructions assume the project has not provided a single executable for your operating system and have installed everything manually as per the Installation instructions.

## Windows 11 users

Look for the file called **run_harvester.bat**
This is a script you can use to change to the directory where you installed everything, activate the python "venv", and then run the harvester.
This script assumes you used our example in Installation to put everything in Documents\COUNTER_Harvester, so you have a folder inside that called "venv" and another folder called "src".
If you put everything somewhere else, edit that script file to change the PROJECT_DIR to wherever you put it.

If you did not create a venv but just put all of the requirements.txt modules directly into your python installation, delete or comment out the script lines from "echo Activating the Python virtual environment..."  to the line right before: "echo Changing directory to the 'src' folder...".

You can put the run_harvester.bat anywhere you like and create a link to it on your Desktop or other convenient location. Ask your local Windows tech for help doing that if you aren't sure how to do that.![![]()]()

## non-Windows users
After you've set up the current_config.py and providers.tsv to your needs, you simply run the program with this command line:
python3 main.py     (depending on your operating system, you might leave off the "3").

You may do that using a command line window or you may be able to set up a desktop icon to do that for you.
If you needed to create a "virtual environment" for the harvester so the dependency packages do not interfere with other python programs you use, you may want to create a desktop shortcut to a script that does all of those steps for you (change directory to where the program is installed, activate the virtual environment, then start the program).

## Running the Harvester - Using the Graphical User Interface (GUI)

The GUI allows you to set all of the relevant options for each time you want to run it. Running a "harvest" means setting up all of these options as you want them, and then clicking the Start button to start retrieving the desired reports.

- The** start and end dates** to request the data for. Use the pick lists to select the settings.
--The start date default is set in the current_config.py file (which you can easily modify using the Settings button) so you can change it as fits your workflow. For instance, throughout 2025, you may want the start date to always default to January 2025, then in 2026, you may want your start date to always default to January 2026.
-- The end data always defaults to the month before the current one, a per the COUNTER standard that data is always provided in full months, so the latest possible data is always in the next month, eg January 2026 data will not be available until February 2026. Note further that providers have until 28 days into the new month so January 2026 data may be not available until February 28, 2026, although many providers release their data much sooner into the new month than that.
– You can easily override the defaults for any specific harvest run using the month and year boxes provided.

The harvester checks the date range available from each provider compared to your request and adjusts the range per provider to only include YYYY-MM that the provider supports (and warns you of any adjustments in the progress log and the error log).

- **Providers**: You can select any or all of the providers to include in this run using the checkboxes provided. This list comes from the providers.tsv file. 
- **Report Type**s: You can select any or all of the report types to include in this run using the checkboxes provided.
- - The harvester will check your list of requested report types against what that provider's API server tells it are the supported report types and only request the supported ones.

When you press the Start button, it just runs until it is done. Depending on how many providers have required delays and retries, it could take a few minutes or even hours, as it processes each report request fully one at a time, especially if some providers require delays between requests and/or retries.

### Progress Log

You will see a "Harvester Progress" window while it is running.
The progress log will display warnings for problems that you probably want to know about, especially if a provider/report won't have the data you asked for, e.g., unsupported report types, or data not available for that date range.

You can stop the harvester while it is running, by using the STOP button. However, that will not undo whatever was saved to that point, including json and tsv files, and data saved in the sqlite database.

Once the harvest is complete or you stopped it, you can save the messages in the progress window to a file to review later by clicking on Save Progress Output.

## Information Log
In addition to the progress log, which you can save to look through further later, there is also a more detailed **info_log.txt** file, which is a plain text file with much more detail about every individual API call for every report.

The info log file is reset to empty after every run, so copy it to somewhere else before your next run it if you want to examine it. It will have much more detailed data than the progess log and may help you troubleshoot problems with individual providers.  

It includes the actual URLs used for every report request. You can paste a COUNTER API URL directly into your favorite web browser to see if it works, and if there was a problem with it. If it returns anything other than a generic HTTP error, that response will be in json.  You can share that link with that provider's tech support or anyone else you have helping you. Just be aware that it contains all of your "credentials" (customer_id, requestor_id, and api_key) and some people consider parts of that to be like "passwords" so think carefully about how you share it.

## What is happening during a harvest run

These are the steps it goes through after you start a harvest run:
1. for each selected provider, run a COUNTER-defined API command to get the list of reports that provider supports (e.g., a journals-only platform probably won't support TR_B1 which is for ebook usage) and then limits the list to the ones you selected
2. fetch the json for each report in that list and save it into its own json file
3. use that json to generate .tsv files just like you would have gotten interactively from the provider's own "institutional dashboard" website
4. use that same json data again to add the specific metric data to the sqlite database to run more complex searches than you can do in an individual spreadsheet

Read the [SQLITE Database](sqlite_database_info.md) document to learn more about that.

## Manage Providers

The GUI provides you with the option to add, remove, or edit your provider information interactively, one entry at a time.
You can also choose to edit the providers.tsv file directly using an appropriate editor.  
The GUI indicates the required fields with an asterisk next to their labels. Specific providers may choose to require any or all of the rest of the fields.
Changes take effect when you click on the Save Provider button.
See the "[Providers template file](template%20providers%20explanation.md)" document for more information about provider information, and "[Provider specific quirks - Retries and Delays](provider_specific_notes.md)" for explanation about some special cases to be cognizant of.

## Settings

The "Settings" button gives you a graphical window to modify the values in the "current_config.py" file. 
It also gives the option to "reset to defaults" which will revert all values to what they were when you first installed the harvester. More specifically, it reverts to the values in the default_config.py file, so if you manually edit that (we do not recommend that), that is what the reset button will reset to.
If you make a change and forget to click on the Save button before closing the Settings window, you will be prompted whether to "save and close" or "close without saving".
If you save any changes, they will take effect for the next harvest run that you might run now, and will remain set the next time you run the program.
See the "[Configuration options](config-options.md)" document for more explanation regarding what all of the settings are for.

## Help
The main window's Help button pops up a basic list of what to do.

The Help buttons on Manage Providers and Settings take you to relevant pages in the repository documentation.
They will open a new tab on your default browser.