# Steps to get this running

This document assumes that we have not yet provided an executable package for your operating system and need to install the harvester manually.

## Step 1 - create a folder/directory on your hard drive that you want everything to go into
Decide where on your hard drive you want all of this, the code and reports, to be stored. Everything will stay in that one folder/directory tree. For instance, you might want to make a folder within your "My Documents" called "COUNTER_Harvester", so create that. You can call it whatever you like. All of the program's files and all of the files that it creates with your COUNTER data will be within that folder.

## Step 2 - Download the harvester package
* On the repository starting page, find the green Code menu pulldown - open it then click on Download zip and save the file to the folder you created for it.
* Unzip the downloaded zip file directly into that folder. How to do that depends on how your operating system (Windows, Mac) is configured, but you can probably "unzip" it using your usual file browser, then right-click on the zip filename and select "extract" or "unzip" from the context menu that pops up.
  
## Step 3 - Make sure you have Python3 and the required packages installed

This is written entirely in python (python 3), so it will run on Windows, Mac, and Linux. It was developed and tested on all three.

Python is an "interpreted" language, which means you just need to make sure you have python3 and the required "packages' installed, and put all of the python program files in a directory anywhere you want it on your computer, and it will make all of the files and subfolders relative to wherever you put it.
The harvester itself does not touch any of your system files or settings, so no settings in your Windows registry or files in the "Program Files" folder.

Python files end with **.py** and are plain text, so you can view and edit them in a plain text editor, like Notepad in Windows, 
or Textedit in Mac OS (use Shift-Cmd-T to make sure you are not adding rich text format to the file)

Python can be downloaded from: (https://www.python.org/downloads/)

Get the latest stable version (ie not "pre-release" status one).

Mac users may find they already have it, but make sure you have Python 3, not Python 2.

There are a few third-party packages required to be installed separately. They are in **the requirements.txt** file.
The python utility that helps you install third-party packages is called **pip**. In some cases, you need to call it **pip3** for python 3.

Here is how you use pip. From a command line window/terminal/shell in the folder where you unzipped this project:
**pip install -r requirements.txt**
If that gives you an error that pip doesn't exist, use:   **pip3 install -r requirements.txt**

If you are python-savvy, you can also just read the requirements.txt (plain text file) and use **pip install** [packagename] to install each separately.

Advanced tip: if you use python for other things, make a python "**venv**" virtual environment for the harvester and run pip when you are inside that.

Basic steps for building and using a "venv" that using a command shell/window, starting in the folder where you unzipped the harvester:

1. Do this just once:
- python -m venv venv        - this builds the virtual environment (may need to be python3 as in steps above)

2. Do these every time you run the harvester, and do them right after the above step to install the requirements:
- source venv/bin/activate    - for Linux and Mac
- venv\Scripts\activate        - for Windows

3. Do the appropriate "pip" command from above just once after you have activated the "venv" environment.


## Step 4 - set up the providers.tsv file with your site's COUNTER 5.1 information and (optional) change the current_config.py values to what you want

Run the harvester, and use the Settings button to change the default settings.  You can leave all of these alone if you like.
All of these options are explained in the configuration options document here.

If you are going to change any of the options that refer to file, folder, or table names, make those changes before you start your first data harvest.

Then use the Manage Providers to set up the providers.tsv file with the information about your providers and your credentials (eg customer_id, requestor_id, api_key).
You can get the base_url and some information about how to get the rest from the [COUNTER Registry](https://registry.countermetrics.org/). Optionally, you can edit this file directly using whatever program you like to use for tab-separated-value (tsv) files. But be sure you save it in tsv format, not Excel or odt, or any other format.

You will find a template file you can download and use as your starting file called template_providers.tsv right here.

For more information about what the harvester creates, see the What is saved where document.
