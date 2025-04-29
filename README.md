# C5.1_Harvester
Python code to harvest COUNTER Metrics usage data reports using the SUSHI API, generate the TSV files and store it in an sqlite database

This does not have a graphical user interface, just a command line one, but it is very simple to use.
It just needs you to maintain a tsv file with the info about your providers' SUSHI information.
When it is run, you will be asked for starting and ending dates, and then it does the rest.
There is a sushiconfig.py file that gives you a few basic configuration choices.

As of April 29, 2025, it supports all PR, DR, and TR reports and views, but not the IRs yet.
I hope to have the IRs working by the end of the year, once I can find some valid (passed audit) IRs from one of UPEI's providers to test with.

I am the sole creator and maintainer of this code. If anyone would be interested in getting involved, contact me at mbelvadi@upei.ca

See the docs for more information.

- Melissa Belvadi, librarian at the University of Prince Edward Island
