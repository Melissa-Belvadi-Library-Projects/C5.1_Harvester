After you've set up the sushiconfig.py and providers.tsv to your needs, you simply run the program with this command line:
python3 getcounter.py     (depending on your operating system, you might leave off the "3")

It will ask you for begin and end dates for the data months you want to harvest.

It defaults to the first official date for COP5.1, which is January 2025, for the begin date, so just pressing Enter will give you that.

It defaults to the month before the current month you are running it in for the end date, so if you are running it in May 2025, the default end date will be April 2025 if
you just press Enter.

You can of course enter other start and end dates, both in YYYY-MM format.

It checks the date range available compared to your request and adjusts the range per provider to only include YYYY-MM that the provider supports (and tells you this in the console and the errorlog).

May 12, 2025 Update: It will also ask if you want to get just one specific report or view (for all providers in the tsv file) or all of them.

Then  it just runs until it's done. It puts some basic progress information in the running window, and will give special notice there for 
  problems that you probably want to know about, especially if a provider/report won't have the data you asked for.

In python, errors that the program can catch and deal with and not have the whole program simply "crash" are called "Exceptions".
Exceptions usually do mean giving up on the steps for that report or even entire provider, but usually don't end the program completely.

The most common examples of that are if there is no data/usage for some or all of the date range you specified.

There is also an errorlog.txt file (file name can be changed in sushiconfig.py) that is reset to empty after every run, that will have more data that may help you troubleshoot problems with individual providers.

It always starts by giving you all of the URLs for all of the report types for all of the providers. You can actually paste a SUSHI API URL directly into your web browser to
see if it works, if there was a problem with it, and you can share that with the the providers tech support or anyone else you have helping you; just be aware that it contains all of
your "credentials" and some people consider parts of that to be like "passwords" so think carefully about where you share it.

The error log is simply a plain text file so if you want to save it for later analysis but keep running the Harvester with other providers, you can easily just make a copy of it wherever you want it.
The error log also contains INFO and Warning lines that may help you, in addition to the ERROR lines that report a true problem, usually on the provider's side.

These are the steps it goes through:
1. read in all of your providers info<br>
2. for each provider, run the API command to get the list of reports that provider supports (eg a journals-only platform won't support TR_B1 which is for books)<br>
3. fetch the json for each supported report and save it into its own json file (see docs/files_and_folders)<br>
4. use that json to generate .tsv files just like you would have gotten interactively from the provider's own "institutional admin" website<br>
5. use that data again to populate/add to an sqlite database for using to run more complex searches than you can do in an individual spreadsheet (see docs/sqlite_database_info)<br>
