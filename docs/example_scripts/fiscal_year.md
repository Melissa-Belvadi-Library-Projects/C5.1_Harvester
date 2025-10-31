How to sum metric usage data by a fiscal year instead of calendar year - uses the example of 2024 May - 2025 April cycle:

```SQL
select Platform, sum(Metric_Usage) as UIR from PR where
Provider_Name like 'Gale' and
Data_Type like 'Journal' and
Metric_Type like 'Unique_Item_Requests' and
(Data_Year * 100 + Data_Month) BETWEEN 202405 AND 202504
group by Platform;
```
