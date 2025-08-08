Documentation about how to install and use this program is in this directory.

Here is a quick intro to some of the jargon involved. This is intended for librarians, so don't be intimidated!

# What is COUNTER 5.1?
An international organization called [COUNTER Metrics](https://www.countermetrics.org/) provides an industry-wide standard (common set of rules) for the electronic books, journals, databases, etc. industry that licenses such resources to libraries.  Those rules define specific ways to count how our patrons use those resources, and they tell the publisher/content provider how they should report that data.

The COUNTER Code of Practice ("COP") 5.1 is the latest version of those rules. It became required for content providers that claim to its customers to be "COUNTER-compliant" in January 2025.
There is no law forcing providers to follow COUNTER rules, and some don't, especially smaller ones with very specialized kinds of content that don't fit well with COUNTER rules. But all of the major academic publishers and aggregator platforms (EBSCO, Proquest, Gale, JSTOR, etc.) do offer COUNTER-compliant reports. Everyone following the same rules allows librarians to compare usage across different providers.

# How does a librarian get their 5.1 usage data?

COP 5.1 provides specific definitions for 16 different kinds of [reports](https://www.countermetrics.org/education/reports/).  Those reports should be available to that provider's library customers in two ways. First is  a downloadable spreadsheet friendly file, using either Excel format (.xlsx) or a tab-delimited file (usually .tsv although some providers might give it a .txt filename extension). Librarians can download these files one at a time from some kind of account website the provider has arranged for them to use. Keep reading to learn about the second way.

## What is an API and what is JSON?

The second is more technical. The provider needs to run a special kind of web-based server called a "SUSHI API" server that can send the data back to the user in a very specific format called "json".  The API server is just like a web server in that you can ask it for the data using a URL in your normal web browser.  However, you will not want to try to read what you get back. JSON format is not meant for humans to read. It is meant for software like this harvester to "read" and convert into human-readable reports.

The content providers will give each of their library customers specific codes, kind of like "login credentials" for the account website, that are used specifically with the API.

This "harvester" program is an "API client" that retrieves data from all of the "API servers" that you have accounts with through your content providers.

# Why would I want to use this harvester program?

## Save time downloading all of the reports you want

If you are tasked with downloading all of the COUNTER reports for all of your content providers, you know how incredibly time-consuming that is.  This program allows you to give it a list of all of your COP 5.1-compliant providers along with the "login credentials" they gave you, and then tell it to just go get all of the reports, and it gets them all for you over a few minutes and saves the ".tsv" files for you on your computer. You can specify what months of usage data you want.

## Do advanced analysis on your usage data

There is a bit more detail about using it in the documents in this repository "docs" folder.  And there's another advanced feature that it offers if you want to use it - it puts all of that usage data into a single file on your computer in a format called "sqlite". That's a database that you can use to analyze your data across multiple years and multiple providers in ways that are much too hard for most people to do when all of the data for each provider is in its own separate spreadsheet file.

# Learn More...

The other documents in this folder in github explain much more detail about all of this.
If you are new to COUNTER Metrics, there are many wonderful [friendly guides for librarians](https://www.countermetrics.org/education/) and other information to help you make the most of your library's usage data.

## Which of our providers can we use this with?

COUNTER Metrics maintains a [Registry](https://registry.countermetrics.org/) that lists all of the content providers that are COUNTER-compliant or are in the middle of being audited to be recognized as compliant.
You can get some useful information there about what settings you need to use with this harvester to access that provider's usage data for you.
