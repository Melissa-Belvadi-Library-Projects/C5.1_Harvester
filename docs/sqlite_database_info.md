This document explains the structure of the sqlite database and how to use it. Example sql scripts for it are in the example-scripts documentation folder in this repository.

>May 12, 2025 update: the 1.0 version has significant changes to the database structure and is not compatible with one made by 0.9. Fortunately you can simply rename the old one, and re-run all reports to populate the new one without losing any data beause providers under the COUNTER rules must provide 2 years + current year available for re-fetching

- The sqlite database is a single file, by default called counterdata.db but you can change it in sushiconfig.py.
  - There is no server involved; for Windows users it's very much like a Microsoft Access database.
- It resides in the main folder for the Harvester.
- All of its data comes from the EX versions of the 4 reports - PR, DR, TR, and IR, but the Report_Type column uses the two-letter Report_Type.
- There is just one table, usage_data. To see how usage_data is defined, look at create_tables.py.

An sqlite database can be queried in a number of ways. There is a command-line sqlite interface, which you can download for Windows, Mac, and Linux at:
(https://sqlite.org/download.html)

But there are lots of better options using graphical interfaces.
  If you have Microsoft Access, you can open an sqlite database with that.  There are lots of videos and web pages about how to do that.

I recommend a free program that is available on Windows, Mac, and Linux called dbeaver: (https://dbeaver.io/)
There is a free version that works just fine for this purpose.

The usage_data table is set up to only store 1 row per unique combination of the settings, using a hash text that also handles null values.

If you download the "same" data (same metric, provider, month-year, title/database/platform etc.)  more than once, it will overwrite ("replace") rather than add.
That way, you'll always have the most recently available metrics, as it often happens that a provider will tell its customers "sorry we messed up our data, please
download it again" and all you'd need to do is just re-run the Harvester with that provider in providers.tsv and the appropriate date range.

The point of the "EX" special reports is to make sure this data has the maximal breakdown by all possible "attributes", eg Access_Method for PR and DR, and YOP, Access_Type, and Access_Method
for TR. So when you don't care about the YOP, you'll use an aggregator function like "SUM' to combine the usage.  There are examples of how to do this in the example-scripts folder in
this repository docs.

Unless you deliberately move/remove the db file, it will continue to collect non-duplicative data for the entire life of COP5.1, so you can, for instance, find all of the uses (or denials)
of a given title/issn/etc. across many vendors and across many years.  ISBNs can be more difficult because although there is an official standard for hyphenation, vendors often violate it
in their COUNTER reports.  There is a script example that will show you how to strip out the hyphens within a search across vendors.

  The sqlite database is just an ordinary file. And the Harvester will start a new one if you move/rename the existing one. So you can share this file, create separate ones by moving past-created
ones to other folders, make backups using your usual operating system file backup routine, and so forth as needed.
  
  
