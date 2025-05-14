# C5.1_Harvester
Python code to harvest COUNTER Metrics usage data reports using the SUSHI API, generate the TSV files and store the data in an sqlite database.

This does not have a graphical user interface, just a command line one, but it is very simple to use.
It just needs you to maintain a tsv file with the info about your providers' SUSHI information.
When it is run, you will be asked for starting and ending dates, and whether you want just one report/view or all of them, and then it does the rest.
There is a sushiconfig.py file that gives you a few basic configuration choices.

As of May 12, 2025, it supports all PR, DR, IR, and TR reports and views.

I am the sole creator and maintainer of this code. If anyone would be interested in getting involved, contact me at mbelvadi@upei.ca

See the docs for more information.

For more information about COUNTER Metrics and the reports, see the [Education section of COUNTER's website](https://www.countermetrics.org/education/)

- Melissa Belvadi, librarian at the University of Prince Edward Island
