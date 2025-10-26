# SQL Scripts for IR Reports

IR reports provide usage at the level of item, which is either a multimedia object, or is an individual journal article.

The multimedia ones are basically just like journal titles.

But the article ones come along with detailed information about their "parent', which is the journal the article is from.

## Top articles used, grouped by Journal across all platforms

```sql
select Item, Authors, Article_Version, Publisher, Parent_Title, Parent_Online_ISSN, Parent_Publication_Date, sum(Metric_Usage) as Uses, Metric_Type
FROM IR
where Metric_Type like 'Unique_Item_Requests' AND Data_Type = 'Article'
AND (Data_Year * 100 + Data_Month) BETWEEN 202405 AND 202504
GROUP BY Parent_Title, Parent_Publication_Date, Item
ORDER BY Uses desc, Parent_Title, Parent_Publication_Date, Item;
```

## Top articles used, group by Journal per platform

```sql
select Platform, Item, Authors, Article_Version, Publisher, Parent_Title, Parent_Online_ISSN, Parent_Publication_Date, sum(Metric_Usage) as Uses, Metric_Type
FROM IR
where Metric_Type like 'Unique_Item_Requests' AND Data_Type = 'Article'
AND (Data_Year * 100 + Data_Month) BETWEEN 202405 AND 202504
GROUP BY Platform, Parent_Title, Parent_Publication_Date, Item
ORDER BY Uses desc, Platform, Parent_Title, Parent_Publication_Date, Item;
```

## Total uses across platforms by media type

```sql
SELECT Data_Type, Metric_Type, SUM(Metric_Usage) AS Reporting_Period_Total
FROM IR
WHERE Access_Method = "Regular"
AND Data_Type in ('Audiovisual','Image','Interactive_Resource','Multimedia','Sound')
AND Metric_Type in ('Unique_Item_Requests')
AND 
(Data_Year * 100 + Data_Month) BETWEEN 202305 AND 202504
GROUP BY Data_Type, Metric_Type
ORDER BY Data_Type, Metric_Type;
```

## Total uses by media type per platform:

```sql
SELECT Platform, Data_Type, Metric_Type, SUM(Metric_Usage) AS Reporting_Period_Total
FROM IR
WHERE Access_Method = "Regular"
AND Data_Type in ('Audiovisual','Image','Interactive_Resource','Multimedia','Sound')
AND Metric_Type in ('Unique_Item_Requests')
AND 
(Data_Year * 100 + Data_Month) BETWEEN 202305 AND 202504
GROUP BY Platform, Data_Type, Metric_Type
ORDER BY Platform, Data_Type, Metric_Type;
```