How to sum metric usage data by a fiscal year instead of calendar year - uses the example of May - April cycle:

`select Platform, sum(Metric_Usage) as UIR from PR where
Provider_Name like 'Gale' and
Data_Type like 'Journal' and
Metric_Type like 'Unique_Item_Requests' and
((Data_Year = 2024 and Data_Month in (5,6,7,8,9,10,11,12))
OR(Data_Year = 2025 and Data_Month in (1,2,3,4)))
group by Platform;`
