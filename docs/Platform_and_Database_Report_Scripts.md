# SQL Scripts for Platform and Database Reports

DR report: Summary of most searches ("searches_regular") by database for all platforms.
Note that if you use a discovery service, you may see really odd results at the top of this list:

`select Platform, Database_Name, Data_Year, Data_Type, sum(Metric_Usage) as Searches from usage_data 
where 
Report_Type like 'DR'
and Metric_Type like 'Searches_Regular'
and Access_Method like 'Regular'
and Data_Type like 'Database%'
group by Platform, Database_Name, Data_Type, Data_Year
order by Searches Desc; `

