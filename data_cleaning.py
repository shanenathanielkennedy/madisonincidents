import pandas as pd
pd.options.mode.chained_assignment = None
import re 
import geopandas as gpd

# Data Cleaning and Transformation

df = pd.read_csv('incident_data.csv')

df["date"] = pd.to_datetime(df["date"]) # Converts Date to dt obj

def officer_type(officername):
    officer_prefixes = ["PIO", "Sgt.", "Lt.", "Capt.", "P.O."]
    split_name = officername.split(" ")
    prefix = split_name[0]
    if prefix in officer_prefixes:
        officer_type = prefix
    else:
        officer_type = "Unspecified"
    return officer_type

# Making Officer Type Column
df["officer_type"] = df["officer"].apply(officer_type)
df["officer_type"] = df["officer_type"].str.replace("PIO", "Public Information Officer")
df["officer_type"] = df["officer_type"].str.replace("P.O.", "Police Officer")
df["officer_type"] = df["officer_type"].str.replace("Sgt.", "Sergeant")
df["officer_type"] = df["officer_type"].str.replace("Lt.", "Lieutenant")
df["officer_type"] = df["officer_type"].str.replace("Capt.", "Captain")

def parse_release(description): # Making Published Time column
    time_and_officer = description.split("Released ")[-1].split("at ")[-1]
    release_time = time_and_officer.split(" by")[0]
    return release_time
    
df["release_time"] = df["description"].apply(parse_release)


def remove_infoline(description): # removing redundant line from incident description
    description = ' '.join(description.split("\n\n")[:-1])
    return description

df["description"] = df["description"].apply(remove_infoline)

# filling NaN updated values (others are dates)
df["updated"].fillna(1)

# Description length column
df["len_desc"] = df["description"].apply(len)

# Preprocessing addressses for geocoding
df["address"] = df["address"].str.replace(" block ", " ")
df["address"] = df["address"].str.replace(" Block ", " ")
df["address"] = df["address"].str.replace("of", "")
df["address"] = df["address"].str.replace(" blk ", " ")

df["address"] = df["address"] + ":Madison, WI"

df["coords"] = gpd.tools.geocode(df["address"], provider="nominatim",user_agent="snkennedy2@wisc.edu")["geometry"]

df.to_csv("incidents_cleaned.csv", index=False)

## Implement Google Geocoding API to geocode ONLY addresses that Nominatim couldn't do (such as intersections)
## Make a feature column ["violent"], 1 for yes, 0 for no


