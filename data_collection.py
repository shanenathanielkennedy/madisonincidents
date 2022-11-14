import report_scraper as rs
import pandas as pd

df = rs.get_incident_data(9999999) 
df.to_csv("incident_data.csv", index=False)