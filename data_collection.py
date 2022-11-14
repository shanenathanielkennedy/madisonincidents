import report_scraper as rs
import pandas as pd

df = rs.get_incident_data(50) # should scrape all the data since 99999
df.to_csv("incident_data.csv")