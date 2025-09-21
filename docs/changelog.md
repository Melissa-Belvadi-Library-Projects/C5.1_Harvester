# Change log
Changes from version 1 to version 2.0:
- Added the GUI using PyQt6, with all of the other changes necessitated by that, including adding dependencies to requirements.txt.
- Switched from using the word "SUSHI" to refer to the API to just referring to it as the "COUNTER API" in alignment with Project COUNTER.

Changes from 0.9, the April pre-release, and 1.0, the May 12, 2025 release:
- Modified sqlite database structure to make updates and new data much faster and eliminated a duplication problem, eg uses hashlib to determine whether need to insert or replace
- added support for IR report and its standard views
  - problem with IR providers not allowing parent_details option raises a problem for future release - IR_A1s are the only way to see the journal name that the article belongs to, but the IR_A1 reports don't get saved into the sqlite database
- added new option at the start of running it, to let you choose to harvest just one specific report type (for all providers in the tsv)
- improved error log messaging and labels, and added a "warning" category of messages there
- added new sushiconfig.py option so you can set the default begin date instead of it defaulting to 2025-01. The end date is still the month before current month that it is running
- added error log warnings if a provider has custom reports (eg Elsevier ScienceDirect). It doesn't yet do anything with those, but lets you know they exist - possible future release
- changed how sqlite data is built by using the tsv instead of rebuilding it all from the original json
- all reports have passed validation via the COUNTER validation tool, except where this harvester specifically indicates it is varying from the COUNTER standard (e.g., allowing you to request empty reports, repeating all metric types in the
- header of all reports even if they are the default
- fixed some problems involving providers that require pauses between API requests or require a second request for the same report ("queuing"), and establishes some sane pauses if one is needed but none provided in the providers tsv
