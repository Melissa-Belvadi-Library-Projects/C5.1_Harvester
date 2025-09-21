# Providers template file

The template file, providers.tsv gives you a starting file, with the columns set up properly and many actual providers' base URL and other settings supplied.
You will need to replace all of the "required" values with your own institutional COUNTER API values. For every provider, that includes the "customer_id". Some providers may require any combination of the requestor_id and api_key as well.  Usually you can get those from the same customer "dashboard" website that you access to download the interactive reports.

  The [COUNTER Registry](https://registry.countermetrics.org/) is where you can find the API data that is not specific to your institution, and usually find a contact email address for each providers along with which credentials are required, and info about the optional columns - platform, delay, retry.

  Note that platform is a COUNTER API specific code that the provider requires. It is NOT a note about who this is, and it does NOT refer to the Usage Data Host that provider may be using   (eg Atypon, ScholarlyIQ, Silverchair, LibLynx, etc.). For instance, Elsevier requires separate platform codes for ScienceDirect ("sd"), Scopus ("sc") and Engineering Village ("ev") usage data, although the base URL and customer credentials are the same for all.

   Some providers like Sage, Taylor & Francis, and Oxford choose to provide entirely different Base URLs and/or credentials for their journal vs book platforms, instead of using the "platform" code. 

  See the "Provider specific quirks" document here for more explanation about the Delay and Retry values.


