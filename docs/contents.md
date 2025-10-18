Documentation for COUNTER 5.1 Harvester
- [What is COUNTER 5.1?](README.md)
- [Installation and pre-run setup](installation.md) - instructions for Windows and Mac installation, including installing python itself
- [Configuration options](config-options.md) - including explanations for everything in the settings (current_config.py)
- [template_providers.tsv](template_providers.md) - a starter file to help you get your API credentials for major providers up and running
- [Provider specific quirks - Retries and Delays](provider_specific_notes.md) - making sense of the Delay and Retry columns in the providers.tsv file
- [Providers starting 5.1 support before January 2025](providers_starting_5.1_earlier_than_2025.md)
- [What is saved where](files_and_folders.md) - where the tsv files and other outputs of the harvester are saved
- [SQLite Database](sqlite_database_info.md) - an explanation of what the SQLite database is, and why it's worth using
- [Example SQLite scripts](example_scripts/README.md) - demonstrations of sql scripts for the harvester's database that may be useful to librarians

Other useful links:
- [COUNTER Metrics](https://www.countermetrics.org/) - official website
- [COUNTER Registry](https://registry.countermetrics.org/) - find information about specific providers' compliance with 5.1
- - see also the separate Registry Harvest python script provided in this repository for getting a tsv-format snapshot of all of the relevant data in the Registry.  This can help you populate your providers.tsv but do not use it directly as that file as it contains a lot of extra data in it.

