# Reproducing Standard Views using SQL queries

Really just the data table, not the header, and only reporting_period_total, not the "monthly details".
To get the monthly details, do a search like the second PR_P1 and then output the result to a spreadsheet, and do a "pivot table" on that.

## PR_P1

The PR_P1 standard view is PR data filtered to
Access_Method=Regular
Metric_Types=Searches_Platform,Total_Item_Requests,Unique_Item_Requests,Unique_Title_Requests

This example sums up the usage for the date range May 2023 (202305) through April 2025 (202504):

```SQL
SELECT Platform, Data_Type, Metric_Type, SUM(Metric_Usage) AS Reporting_Period_Total
FROM PR
WHERE Access_Method = "Regular" and Metric_Type in ('Searches_Platform','Total_Item_Requests','Unique_Item_Requests','Unique_Title_Requests')
AND 
(Data_Year * 100 + Data_Month) BETWEEN 202305 AND 202504
GROUP BY Platform, Data_Type, Metric_Type
ORDER BY Platform, Data_Type, Metric_Type;
```

To generate output that you could then "pivot" on in Excel or Google Sheets to get the per-month totals:

```SQL
SELECT Platform, Data_Type, Metric_Type, Data_Year || '-' || printf('%02d', Data_Month) AS YearMonth, SUM(Metric_Usage) AS Usage
FROM PR
WHERE 
Access_Method = "Regular" 
AND Metric_Type in ('Searches_Platform','Total_Item_Requests','Unique_Item_Requests','Unique_Title_Requests')
GROUP BY Platform, Data_Type, Metric_Type, YearMonth;
```
Or if you prefer the per-month to be formatted in the official COUNTER rule of YYYY-MMM (eg 2025-Mar instead of 2025-03), you can do this, but you will lose the ability for the pivot to sort by year-month since the month abbreviations don't sort correctly (eg 2025-Jan would come after 2025-Feb alphabetically):

```SQL
SELECT Platform, Data_Type, Metric_Type, 
CAST(Data_Year AS TEXT) || '-' ||
CASE Data_Month
WHEN 1 THEN 'Jan'
WHEN 2 THEN 'Feb'
WHEN 3 THEN 'Mar'
WHEN 4 THEN 'Apr'
WHEN 5 THEN 'May'
WHEN 6 THEN 'Jun'
WHEN 7 THEN 'Jul'
WHEN 8 THEN 'Aug'
WHEN 9 THEN 'Sep'
WHEN 10 THEN 'Oct'
WHEN 11 THEN 'Nov'
WHEN 12 THEN 'Dec'
ELSE 'Unk'
END AS YearMonth,
SUM(Metric_Usage) AS Usage
FROM PR
WHERE 
Access_Method = "Regular" 
AND Metric_Type in ('Searches_Platform','Total_Item_Requests','Unique_Item_Requests','Unique_Title_Requests')
GROUP BY Platform, Data_Type, Metric_Type, YearMonth;
```

Build your pivot table as Rows (in this order): 
- Platform, Metric_Type
- Columns: YearMonth
- Values: Usage

and note that there are blanks instead of zeros for YearMonths with no usage for that metric

## DR_D1

Here is the basic select - you can use the techniques in the PR_P1 examples as well for the more advanced outputs

```sql
SELECT Database_Name, Publisher, Publisher_ID, Platform, Proprietary as Proprietary_ID, Metric_Type, SUM(Metric_Usage) AS Reporting_Period_Total
FROM DR
WHERE Access_Method = "Regular" and Metric_Type in ('Searches_Automated','Searches_Federated','Searches_Regular','Total_Item_Investigations','Total_Item_Requests','Unique_Item_Investigations','Unique_Item_Requests')
AND 
(Data_Year * 100 + Data_Month) BETWEEN 202305 AND 202504
GROUP BY Database_Name, Platform, Data_Type, Metric_Type
ORDER BY Database_Name, Platform, Data_Type, Metric_Type;
```

## DR_D2
```sql
SELECT Database_Name, Publisher, Publisher_ID, Platform, Proprietary as Proprietary_ID, Metric_Type, SUM(Metric_Usage) AS Reporting_Period_Total
FROM DR
WHERE Access_Method = "Regular" AND Metric_Type in ('Limit_Exceeded','No_License')
AND 
(Data_Year * 100 + Data_Month) BETWEEN 202305 AND 202504
GROUP BY Database_Name, Platform, Data_Type, Metric_Type
ORDER BY Database_Name, Platform, Data_Type, Metric_Type;
```

## TR_J1

```sql
SELECT Title, Publisher, Publisher_ID, Platform, DOI, Proprietary as Proprietary_ID, Print_ISSN, Online_ISSN, URI, Metric_Type, SUM(Metric_Usage) AS Reporting_Period_Total
FROM TR
WHERE Access_Method = "Regular" AND Access_Type = 'Controlled' AND Data_Type = 'Journal'
AND Metric_Type in ('Total_Item_Requests','Unique_Item_Requests')
AND 
(Data_Year * 100 + Data_Month) BETWEEN 202305 AND 202504
GROUP BY Title, Platform, Online_ISSN, Metric_Type
ORDER BY Title, Platform, Online_ISSN, Metric_Type;
```

**TR_J**2 is identical except: Metric_Type in ('Limit_Exceeded','No_License')

## TR_J3

Changes Access Type and Metric Types

```sql
SELECT Title, Publisher, Publisher_ID, Platform, DOI, Proprietary as Proprietary_ID, Print_ISSN, Online_ISSN, URI, Access_Type, Metric_Type, SUM(Metric_Usage) AS Reporting_Period_Total
FROM TR
WHERE Access_Method = "Regular" AND Data_Type = 'Journal'
AND Metric_Type in ('Total_Item_Investigations','Total_Item_Requests','Unique_Item_Investigations','Unique_Item_Requests')
AND 
(Data_Year * 100 + Data_Month) BETWEEN 202305 AND 202504
GROUP BY Title, Platform, Online_ISSN, Metric_Type
ORDER BY Title, Platform, Online_ISSN, Metric_Type;
```

## TR_J4

Is just like TR_J1 but with the YOP breakdown:

```sql
SELECT Title, Publisher, Publisher_ID, Platform, DOI, Proprietary as Proprietary_ID, Print_ISSN, Online_ISSN, URI, YOP, Metric_Type, SUM(Metric_Usage) AS Reporting_Period_Total
FROM TR
WHERE Access_Method = "Regular" AND Access_Type = 'Controlled' AND Data_Type = 'Journal'
AND Metric_Type in ('Total_Item_Requests','Unique_Item_Requests')
AND 
(Data_Year * 100 + Data_Month) BETWEEN 202305 AND 202504
GROUP BY Title, Platform, Online_ISSN, Metric_Type
ORDER BY Title, Platform, Online_ISSN, Metric_Type;
```

## TR_B1

```sql
SELECT Title, Publisher, Publisher_ID, Platform, DOI, Proprietary as Proprietary_ID, ISBN, Print_ISSN, Online_ISSN, URI, Data_Type, YOP, Metric_Type, SUM(Metric_Usage) AS Reporting_Period_Total
FROM TR
WHERE Access_Method = "Regular" AND Access_Type = 'Controlled' AND Data_Type in ('Book','Reference Work')
AND Metric_Type in ('Total_Item_Requests','Unique_Title_Requests')
AND 
(Data_Year * 100 + Data_Month) BETWEEN 202305 AND 202504
GROUP BY Title, Platform, ISBN, Metric_Type
ORDER BY Title, Platform, ISBN, Metric_Type;
```

## TR_B2

```sql
SELECT Title, Publisher, Publisher_ID, Platform, DOI, Proprietary as Proprietary_ID, ISBN, Print_ISSN, Online_ISSN, URI, Data_Type, YOP, Metric_Type, SUM(Metric_Usage) AS Reporting_Period_Total
FROM TR
WHERE Access_Method = "Regular" AND Data_Type in ('Book','Reference Work')
AND Metric_Type in ('Limit_Exceeded','No_License')
AND 
(Data_Year * 100 + Data_Month) BETWEEN 202305 AND 202504
GROUP BY Title, Platform, ISBN, Metric_Type
ORDER BY Title, Platform, ISBN, Metric_Type;
```

## TR_B3

```sql
SELECT Title, Publisher, Publisher_ID, Platform, DOI, Proprietary as Proprietary_ID, ISBN, Print_ISSN, Online_ISSN, URI, Data_Type, YOP, Access_Type, Metric_Type, SUM(Metric_Usage) AS Reporting_Period_Total
FROM TR
WHERE Access_Method = "Regular" AND Data_Type in ('Book','Reference Work')
AND Metric_Type in ('Total_Item_Investigations','Total_Item_Requests','Unique_Item_Investigations','Unique_Item_Requests', 'Unique_Title_Investigations','Unique_Title_Requests')
AND 
(Data_Year * 100 + Data_Month) BETWEEN 202305 AND 202504
GROUP BY Title, Platform, ISBN, Metric_Type
ORDER BY Title, Platform, ISBN, Metric_Type;
```

## IR_A1

IR_A1 is unusual in being the only standard view that has MORE data than the standard IR (by default does not have the parent info). But the Harvester captures all of that data using the "IR_EX" API call.

```sql
SELECT Item, Publisher, Publisher_ID, Platform, Authors, Publication_Date, Article_Version, DOI, Proprietary as Proprietary_ID, Print_ISSN, Online_ISSN, URI, Parent_Title, Parent_Authors, Parent_Article_Version, Parent_DOI, Parent_Proprietary_ID, Parent_Print_ISSN, Parent_Online_ISSN, Parent_URI, Access_Type, Metric_Type, SUM(Metric_Usage) AS Reporting_Period_Total
FROM IR
WHERE Access_Method = "Regular" AND Data_Type = 'Article'
AND Metric_Type in ('Total_Item_Requests','Unique_Item_Requests')
AND 
(Data_Year * 100 + Data_Month) BETWEEN 202305 AND 202504
GROUP BY Item, Platform, Publication_Date, Online_ISSN, Metric_Type
ORDER BY Item, Platform, Publication_Date, Online_ISSN, Metric_Type;
```

## IR_M1

```sql
SELECT Item, Publisher, Publisher_ID, Platform, DOI, Proprietary as Proprietary_ID, URI, Data_Type, Metric_Type, SUM(Metric_Usage) AS Reporting_Period_Total
FROM IR
WHERE Access_Method = "Regular"
AND Data_Type in ('Audiovisual','Image','Interactive_Resource','Multimedia','Sound')
AND Metric_Type in ('Total_Item_Requests','Unique_Item_Requests')
AND 
(Data_Year * 100 + Data_Month) BETWEEN 202305 AND 202504
GROUP BY Item, Platform, Publication_Date, Online_ISSN, Metric_Type
ORDER BY Item, Platform, Publication_Date, Online_ISSN, Metric_Type;
```