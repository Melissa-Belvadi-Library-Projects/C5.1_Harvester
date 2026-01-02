This folder includes example SQL scripts for the sqlite database that this project stores data in.

This will be a work in progress, and requests for scripts to do specific tasks should be sent to Melissa. 

The LLM GenAI systems, especially ChatGPT4 and Claude 3.7, are VERY good at writing complex sqlite queries, but you have to know enough to be very specific about what you want. They give you better answers if you tell them your actual table name, column names, relevant filter values on those columns, etc. so you don't have to replace "your_table" etc. in the proferred script.

If you want to write scripts in an editor like MS Word, be careful not to let it use "smart quotes" because that will break your sql code. Smart quotes are when the open and closing quotation marks are curled inward instead of being identical characters.

[Title Report Scripts](title-related-scripts.md) including:
- Top titles report
- Book Title investigations without full text requests
- Journal title investigations without full text requests across multiple platforms without regard for YOP
- Journal title denials with YOP breakdown (eg for considering backfile purchases)
- Book title denials across multiple platforms
- Book usage across two platforms by title

[Platform and Database Report Scripts](Platform_and_Database_Report_Scripts.md):
- DR report: Summary of most searches ("searches_regular") by database for all platforms
- PR report: steps to combine a harvest with an sql query and then a pivot in a spreadsheet to make sure you have harvested all available data from each provider

[IR Report Scripts](SQL_Scripts_for_IR_Reports.md)
- Top articles used, grouped by Journal across all platforms
- Top articles used, group by Journal per platform
- Total uses across platforms by media type
- Total uses by media type per platform

[Fiscal year date range example](fiscal_year.md)

[Multi-report scripts and other advanced tricks](sample_scripts.md) - how to use a CASE statement instead of a lot of if/else, UNION across report types, and more

[Reproducing standard views](standard_views.md) - examples showing how to mostly imitate the filters, attributes, and metric types of the standard view (e.g. PR_P1, TR_J1, etc.)
- This provides lots of examples of scripts using various features of the 4 tables and more examples of some of the advanced script techniques like CASE, combining year-month into a simpler column, and more

[Comparing "open" and "controlled" usage](open_vs_controlled.md) - some really advanced sql scripting techniques to help you analyze by provider and year how much of your usage is open access vs controlled (paywalled) access.
