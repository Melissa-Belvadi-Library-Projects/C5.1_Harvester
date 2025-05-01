    ### Move the dates out of Report_Filters and into Reporting_Period
    ##### and then format the rest of Report_Filters properly for the report_filters header string value

### data parameter should be the Report Filters dict

def reporting_period_build(data):

    if isinstance(data, dict):
        begin_date = data.get('Begin_Date', '')
        end_date = data.get('End_Date', '')
        reporting_period = f"Begin_Date={begin_date}; End_Date={end_date}"
        return reporting_period
    else:
        return ''
