# SQL Scripts for Platform and Database Reports

### DR summary of searches by database

DR report: Summary of most searches ("searches_regular") by database for all platforms.
Note that if you use a discovery service, you may see really odd results at the top of this list:

`select Platform, Database_Name, Data_Year, Data_Type, sum(Metric_Usage) as Searches from DR 
where 
Metric_Type like 'Searches_Regular'
and Access_Method like 'Regular'
and Data_Type like 'Database%'
group by Platform, Database_Name, Data_Type, Data_Year
order by Searches Desc; `

### PR Check that you've harvested all possible years/months for all providers
To make sure you've harvested all of the available reports for all providers:
1. Do a harvester run of all providers back to January 2010 for the PR report. No providers go that far back for COP 5.1, so you'll get a warning with each one's actual start month for every one of them
2. Then use this sql query in your counterdata.db:
```
select distinct Provider_Name, Data_Year, Data_Month from PR order by Provider_Name, Data_Year, Data_Month ;
```
Every provider should be supporting PR at minimum.

3. Take the results of that as csv/tsv output, put it into a spreadsheet, create a pivot table with Provider_Name as the rows (main sort) and Data_Year as the columns (sorted descending) and COUNTA on Provider_Name as the values. You will get a table that shows for each provider the number of months retrieved for each year. For instance, Annual Reviews starts providing 5.1 data with 2024-04, so if you've gotten all of the possible months (assuming you have usage for all months), you'll see a "9" in the 2024 column for the Annual Reviews row.

4. You can cross-check that against what the starting date should be for each provider by checking each of your provider's available reports info near the top of the infolog.txt file. (Make sure to save this info into another file before you run another harvest as infolog.txt gets overwritten on each run.)

For example, for Annual Reports, you will see something like this:
```
INFO: Annual_Reviews: supported reports API URL=https://www.annualreviews.org/counter5/sushi/r51/reports?customer_id=123456&requestor_id=123456
INFO: Annual_Reviews: supported reports: IR,IR_A1,PR,PR_P1,TR,TR_J1,TR_J2,TR_J3,TR_J4
WARNING: Data for Annual_Reviews will not start until 2024-04
```
Note that for Elsevier platforms, you will need to have done the PR harvest in 3-year increments starting with 2015-01 to get all possible data for all platforms before you do the sql query etc. here. See [the doc here regarding platforms that go back before 2025](https://github.com/Melissa-Belvadi-Library-Projects/C5.1_Harvester/blob/main/docs/providers_starting_5.1_earlier_than_2025.md) for a further explanation about Elsevier data.

5. You can then repeat this sequence as needed for the other main reports (DR, TR, IR) to make sure you've gotten all possible data for all report types, keeping in mind that some platforms don't support one or more of these (eg Elsevier-Scopus does not support TR) so those will not appear on the relevant pivot table.  In my example above, Annual Reviews does not support DR as you can see from the second "INFO" line.
