# Title Report Scripts

To make the best use of this data, make sure you learn what the various options: metric types, access types and methods, data types, etc. actually mean
COUNTER Metrics has an excellent set of tutorials for librarians at [COUNTER Metrics Education](https://www.countermetrics.org/education/)

## Book Title investigations without full text requests

Find all of the books that had title investigations but no title requests - this tends to mean books your patrons were interested in, but you didn't have the full text, or at least not on that platform:
This example shows how to sum up metric_usage, which is something you'll want to do often. Important to that working is that list of "group by" fields from your select list. The order in the "group by" doesn't matter.
The "as Usage" simply gives a nice display to that column heading in the output instead of the actual formula. 
Be aware of the problem of two books having the same title that are NOT the same book. You can consider using ISBN but often the ISBN for the same book is different on different platforms.

```
select distinct Title , Metric_Type, sum(Metric_Usage) as Usage, YOP, Data_Year  from usage_data ud  
where Report_Type like 'TR' and Metric_Type like 'Unique_Title_Investigations' and Data_Type  like 'Book'
and Title not in (select distinct Title from usage_data ud2  where Metric_Type like '%Requests')
group by Title, Data_Year, YOP;
```

If you want to be specific to a particular provider (so the sum is per provider), you can add to both the select and group by sections the column "Provider_Name". 
But that will not show you if a title was investigated on one platform that didn't have the full text, but another one did.

```
select distinct Title , Metric_Type, sum(Metric_Usage) as Usage, ISBN , YOP, Data_Year, Provider_Name  from usage_data ud  
where Report_Type like 'TR' and Metric_Type like 'Unique_Title_Investigations' and Data_Type  like 'Book'
and Title not in (select distinct Title from usage_data ud2  where Metric_Type like '%Requests')
group by Title, Data_Year, ISBN, YOP, Provider_Name;
```

## Journal title investigations without full text requests across multiple platforms without regard for YOP

```
select distinct Title , Metric_Type, sum(Metric_Usage) as Usage  from usage_data ud  
where Report_Type like 'TR' and Metric_Type like 'Unique_Item_Investigations' and Data_Type  like 'Journal'
and Title not in (select distinct Title from usage_data ud2  where Metric_Type like '%Requests')
group by Title, Provider_Name;
```
