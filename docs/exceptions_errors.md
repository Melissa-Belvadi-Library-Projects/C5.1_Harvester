# Understanding Errors and Exceptions in the info log



## There are basically two kinds of errors you may see in the info log:
- Errors from the python program itself
- Exceptions that are [officially documented](https://countermetrics.stoplight.io/docs/counter-sushi-api/7ccbfsfe7nrev-exception) as part of the COUNTER 5.1 API

One general-purpose trick to try to figure out if the problem is with the python program or the provider's API server is to paste the entire URL into your web browser and see what you get. If you get an HTTP error (400, 500, 404, etc) the problem is definitely with their server (assuming your Base URL is correct). If you get a bunch of odd-looking stuff that starts with a curly bracket, that's a json language response, and the problem may be one of the ones described below.

### Errors from the python program itself:
- These are usually caused by a provider who is providing invalid content including bad json code.
- - An example is when a provider leaves empty an attribute or other COUNTER data field that is not allowed to be empty, such as "Article_Version" in IR reports. That one causes this error: 
`ERROR: Unexpected key=Article_Version, value=`
- - "ERROR: get_json_data failed for this url" - this usually means the provider's API server is failing to respond, or not responding with properly formatted data. We generally recommend to try that one again hours later or maybe a day later and if you are still not getting a response, you could try contacting their tech support.
- In rare cases, you may find an actual bug in the python program. If you are not sure but want to help, please send the text of that entire set of related lines from your infolog.txt to the project maintainers.

### Exceptions that are part of the official COUNTER API:
- These are situations that are basically some restriction or quirk of the particular provider that are allowed by the COUNTER API "rules" but not what most providers do.
- These will typically come with a "message" that helps explain what the problem is
- These generally don't require any fix to the python program, but instead require you to change something in your providers.tsv file or the specific parameters in your harvest run (especially date range and reports requested)
- The most common exceptions are:
- - **3030** "No Usage Available for Requested Dates" This means that your institution has not generated any usage data at all for that provider for that kind of report. 
  - - **3032** "Usage No Longer Available for Requested Dates" - Despite the wording of this, it most often means you have requested too early a start date and that provider just doesn't (and will never have) 5.1 data that far back. Once we are more than 25 months from the Jan 2025 start of COUNTER 5.1 compliance, this message may start to mean what it literally says for the earlier dates you may be requesting. COUNTER only requires providers to keep 2 full years plus the current year available so by January 2028 we will start to see some providers giving this exception for start dates in 2025.
  - - **1011** "Report queued for processing" - this provider requires you to request any particular report twice: the first time starts the generation of the report, and the second actually gets it. Unfortunately most providers are unwilling to guarantee a specific length of time to wait before the second attempt. This error means you should put the integer 2 in the Retry column of providers.tsv for this provider. We generally recommend also using 3 for the Delay, although some providers will not be ready that quickly and you will just have to run that one again a minute or so later.  Generally, "any particular report" means the specific combination of the report type plus the start/end date range.
  - - - All Liblynx-hosted providers and Scholarly IQ-hosted providers require this, so if you see "liblynx" or "scholarlyiq" in the Base URL, be sure to add these numbers to your Delay and Retry columns
     
      If you see a "Code" number that is not on the official documentation list, report it to the provider or to the COUNTER Metrics staff.  Note that Codes 0-999 are allowed as "custom" message codes that any provider can just make up their own message for.  This harvester will not support those as they could change at any time.

