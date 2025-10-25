# Sample Scripts giving examples of more advanced techniques

## Combine available year/month/report_type for all providers and across all report types

Demonstrates use of "Union" - note that for "union" to work, there must be the same number of columns being selected, and usually in the same order

```SQL
select distinct Provider_Name, Data_Year, Data_Month, Report_Type from IR
union
select  distinct Provider_Name, Data_Year, Data_Month, Report_Type  from TR
union
select  distinct Provider_Name, Data_Year, Data_Month, Report_Type  from DR
union
select  distinct Provider_Name, Data_Year, Data_Month, Report_Type  from PR
order by Provider_Name, Data_Year, Data_Month, Report_Type;
```

More advanced version of that demonstrates how to use a "Common Expression Table" (CTE) to create a temporary table that you can then use in the main 'select'
and also how to use CASE for multiple options instead of nesting lots of if/then/else's.

```SQL
with CombinedData as (
select distinct Provider_Name, Data_Year, Data_Month, Report_Type from IR
union
select  distinct Provider_Name, Data_Year, Data_Month, Report_Type  from TR
union
select  distinct Provider_Name, Data_Year, Data_Month, Report_Type  from DR
union
select  distinct Provider_Name, Data_Year, Data_Month, Report_Type  from PR)
select Provider_Name, Report_Type,  Data_Year, 
CASE Data_Month
        WHEN 1  THEN 'Jan'
        WHEN 2  THEN 'Feb'
        WHEN 3  THEN 'Mar'
        WHEN 4  THEN 'Apr'
        WHEN 5  THEN 'May'
        WHEN 6  THEN 'Jun'
        WHEN 7  THEN 'Jul'
        WHEN 8  THEN 'Aug'
        WHEN 9  THEN 'Sep'
        WHEN 10 THEN 'Oct'
        WHEN 11 THEN 'Nov'
        WHEN 12 THEN 'Dec'
        ELSE 'N/A'
    END AS Month_Name
FROM
    CombinedData
order by Provider_Name, Data_Year, Data_Month, Report_Type;
```

