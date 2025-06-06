This is written entirely in python (python 3), so it will run on Windows, Mac, and Linux. It was developed and tested in Ubuntu Linux.

Python is an "interpreted" language, which means you just need to make sure you have python3 and the required "packages' installed, 
and put all of the python program files in a directory anywhere you want it on your computer, and it will make all of the files and subfolders relative to wherever you put it.
The Harvester itself does not touch any of your system files or settings, eg no settings in your Windows registry or "Program Files" folder.

Python files end with **.py** and are plain text, so you can view and edit them in a plain text editor, like Notepad in Windows, 
or Textedit in Mac OS (use Shift-Cmd-T to make sure you are not adding rich text format to the file)

Python can be downloaded from: (https://www.python.org/downloads/)

Get the latest stable version (ie not "pre-release" status).

Mac users may find they already have it, but make sure you have Python 3, not Python 2.

There are just 3 third-party packages required to be installed separately. They are in the requirements.txt file.
The python utility that helps you install third-party packages is called pip. In some cases, you need to call it pip3 for python 3.

Here is how you use pip. From a command line in the folder where you downloaded this entire project including the requirements.txt file:
pip install -r requirements.txt
If that gives you an error, use:   pip3 install -r requirements.txt
You can also just read the requirements.txt (plain text file) and use pip install [packagename] to install each separately.

Advanced tip: if you use python for other things, make a python "venv" virtual environment for the Harvester and run pip when you are inside that.
Basic steps for that, all command lines when you are in the folder where you downloaded the Harvester filed:

- python -m venv venv        - this builds the virtual environment
- source venv/bin/activate    - for Linux and Mac - every time you want to use the virtual environment, ie run the Harvester
- venv\Scripts\activate        - for Windows - every time you want to use the virtual environment, ie run the Harvester

The only setup you need to do after that is to configure the Harvester according to your needs:
Look at the sushiconfig.py file and decide if you want to change any of the default settings.
Do this before you run the Harvester for the first time.

Then set up the providers.tsv file with the information about your providers and your credentials (eg customer_id, requestor_id, api_key).
You can get the base_url and some information about how to get the rest from the [COUNTER Registry](https://registry.countermetrics.org/)

You can maintain multiple providers.tsv files if you want to run the Harvester for just some providers sometimes. The program will always just
add what it gets from the providers at the time you run it - it won't try to delete files or data from providers not currently in the tsv.

For more information about what the Harvester creates, see the next document, Files and Folders.
