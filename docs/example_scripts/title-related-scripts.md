# Title Report Scripts

To make the best use of this data, make sure you learn what the various options: metric types, access types and methods, data types, etc. actually mean
COUNTER Metrics has an excellent set of tutorials for librarians at [COUNTER Metrics Education](https://www.countermetrics.org/education/)

## Top titles report

Find the highest unique_item_requests across all providers, data_types.
You can change the metric type, range of years, specify a particular data_type, etc.

'select Title, sum(Metric_Usage) as Uses, Metric_Type, Data_Type
from usage_data
where Report_Type = 'TR'
and Metric_Type like 'Unique_Item_Requests'
and Data_Year in (2023, 2024, 2025)
group by Title, Data_Type
order by Uses Desc;
'

And then once you identify a particular title that you want to learn more about, eg what platform, you can get all the details with (sample title plugged in, adjusted the metric because it is a book, etc.):
'
select Platform, Title, sum(Metric_Usage) as Uses, Data_Year, Metric_Type, Data_Type
from usage_data
where Report_Type = 'TR'
and Metric_Type like 'Unique_Title_Requests'
and Title like 'The Age of Sustainable Development'
and Data_Type like 'Book'
and Data_Year in (2023, 2024, 2025)
group by Title, Data_Type, Data_Year, Platform, Metric_Type
order by Uses Desc;
'

In general, Unique_Title_Requests is the best metric for books, unless you really want usage for each chapter to count separately, then use Unique_Item_Requests. Unique_Item_Requests is the best for journals.

When using "sum" in the select statement, make sure you list every field that you are outputting, other than that one, in the "group by". 

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

## Book title denials ("No_License")

Find books across all platforms that have one or more turnaways/denials as defined by the COUNTER "No_License" metric, summing up the denials by calendar year. YOP in this situation helps to separate different editions of a book, as the actual edition # may or may not be included in the title. ISBNs are used to distinguish different books with the same title, but that may also have the effect of splintering denials of the same book across two platforms where the platforms do not report the same ISBN (this can happen).

```
select Title, REPLACE(ISBN, '-', '') as ISBN, sum(Metric_Usage) as Denials, Data_Year as Denials,YOP
from usage_data
where
Data_Type like 'Book'
and Report_Type like 'TR'
and Metric_Type like 'No_License'
group by Title, ISBN, Data_Year, YOP
order by Denials Desc, Data_Year;
```

## Book usage across two platforms by title

Find books that have the same title in two different platforms (hopefully the same book) and compare their usage in the two; this sample uses EBSCO and Proquest:

`SELECT ud.Title, ud.metric_usage, ud2.metric_usage, ud.ISBN, ud2.ISBN FROM usage_data ud
join usage_data ud2 on (ud2.Title = ud.Title)
WHERE
ud.Report_Type like 'TR' and ud2.Report_Type like 'TR'
and ud.Metric_Type = 'Unique_Title_Requests'
and ud2.Metric_Type = 'Unique_Title_Requests'
and ud.Provider_Name like 'EBSCO'
and ud2.Provider_Name like 'Proquest_books';
`