# Provider specific quirks - Retries and Delays

Most providers document any non-default API request constraints. 

For instance, they may require every specific report (combination of attribute settings and date range) to be requested twice with a delay between them, so their server can compile the report first.  This is what the "Retry" value in the providers.tsv file is for. You can put a "Y" for yes if the provider doesn't specify a specific delay time, or a number in seconds if they do. The harvester will use a reasonable default value if you put a "Y", but if you have a lot of those, expect the overall time for a harvest run to complete could run long.

Others have a limit on how many API requests you can make over a fixed period of time, so they may not allow you to request all supported reports at the fast speed that the harvester can generate those API calls, but have to deliberately slow down the time between requests. This is what the "Delay" value in the providers.tsv file is for, in seconds.

If a provider requires both of those, a "Y" in "Retry" will cause the harvester to see if there is a number of seconds in the "Delay" column and use that number for the Retry.

Most providers include these limitations in the [Registry](https://registry.countermetrics.org/) entry.  However, some do not but just put the information into report headers as "exceptions". You may have to notice the warnings or error messages (which report the notes in those "exception" fields) when you first run harvests on those providers, and then update your providers.tsv file with that information.

All providers that use Scholarly IQ as their data host require a 1 second delay between all API requests. So for all of these, be sure to put at least "1" in the Delay column for your providers in [this list of SIQ providers](https://registry.countermetrics.org/usage-data-host/436ccfaa-f0dd-4b50-a31f-63005c2feae7). To be safe you might want to use 2 or 3.
