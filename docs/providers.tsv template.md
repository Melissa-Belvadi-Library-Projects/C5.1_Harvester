The template providers.tsv gives you a starting file. The list is the providers that UPEI has, 
and you will need to replace all of the "required" values with your own institutional SUSHI API values.
  Usually you can get those from the same place you go to download the interactive reports.

  The [COUNTER Registry](https://registry.countermetrics.org/) is where you can find the API data that is not specific
  to your institution, and usually find a contact email address for each providers along with which credentials
  are required, and info about the optional columns - platform, delay, retry.

  Note that platform is a SUSHI API specific code that the provider requires. It is NOT a note about who this is, and it does NOT refer to the Usage Data Host that provider may be using
  (eg Atypon, ScholarlyIQ, Silverchair, LibLynx, etc.)

  It can be hard to find the specific number of seconds needed for delay and retry. I'm providing some values as examples, but these are not canonical. The providers should provide that information
  in the Registry and also in the Exception note when you try to request a report via the API that breaches that limit.

  Some providers like Sage, Taylor & Francis, and Oxford choose to provide 
  entirely different Base URLs and/or credentials for their journal vs book platforms, instead of using the "platform" code.
