# C5.1_Harvester
Python code to harvest COUNTER Metrics usage data reports using the SUSHI API, generate the TSV files and store it in an sqlite database

This does not have a graphical user interface, just a command line one, but it is very simple to use.
It just needs you to maintain a tsv file with the info about your providers' SUSHI information.
When it is run, you will be asked for starting and ending dates, and then it does the rest.
There is a sushiconfig.py file that gives you a few basic configuration choices.
