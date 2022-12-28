import pandas as pd
pd.options.mode.chained_assignment = None
import re 
import geopandas as gpd

# Data Cleaning and Transformation
df = pd.read_csv('incident_data.csv')

def officer_type(officername):
    officer_prefixes = ["PIO", "Sgt.", "Lt.", "Capt.", "P.O."]
    split_name = officername.split(" ")
    prefix = split_name[0]
    if prefix in officer_prefixes:
        officer_type = prefix
    else:
        officer_type = "Unspecified"
    return officer_type

# Making Officer Type Column # Fix or suppress FutureWarning
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
df["updated"] = df["updated"].fillna(0)

# Description length column
df["len_desc"] = df["description"].apply(len)

# Preprocessing addressses for geocoding
df["address"] = df["address"].str.replace(" block ", " ")
df["address"] = df["address"].str.replace(" Block ", " ")
df["address"] = df["address"].str.replace(" blk ", " ")
df["address"] = df["address"].str.replace("of", "")

## Remove this block if implementing Google API Geocoding in future!
## For now, it is simply taking the first street of an intersection
## For example, Mifflin St. at Bassett St. simply becomes Millfin St.
## Done this way to avoid losing data, for the purposes of plotting.

df["address"] = df["address"].str.split("/").apply(lambda x: x[0])
df["address"] = df["address"].str.split(" at ").apply(lambda x: x[0])
df["address"] = df["address"].str.split(" and ").apply(lambda x: x[0])

df["address"] = df["address"] + ":Madison, WI"

# Geocoding
geometry = []
for address in df["address"]:
    try:
        point = gpd.tools.geocode(address, provider="nominatim", user_agent="snkennedy2@wisc.edu", timeout=100)["geometry"][0]
    except Exception as e:
        point = None
    geometry.append(point)

df["coords"] = geometry
## Possibly implement Google Geocoding API to geocode ONLY addresses that Nominatim couldn't do (such as intersections)
# Seeing if incidents involve violence, drugs, the university, gangs.
def violent_crime(crime): 
    if crime in ["Robbery", "Murder/Homicide", "Residential Burglary", "Battery", "Sexual Assault",
                 "Non-Residential Burglary", "Fight (In Progress)", "Attempted Homicide", "Child Abuse"]:
        return 1
    return 0

df["violent"] = df["incident"].apply(violent_crime)

def university(description): 
    if "university" in description.lower():
        return 1
    return 0

df["univ"] = df["description"].apply(university)

def drug(description):
    drug_related = ["drug", "thc", "heroin", "methamphetamine", "alcohol", "cocaine", "fentanyl", 
                    "drugs", "marijuana", "cannabis", "psilocybin", "lsd", "dmt", "pcp", "ketamine"]
    if any(word in description.lower() for word in drug_related):
        return 1 
    return 0

df["drug"] = df["description"].apply(drug)

def gang(description):
    if "gang" in description.lower() or "gangs" in description.lower():
        return 1
    return 0

df["gang"] = df["description"].apply(gang)

df.to_csv("incidents_cleaned.csv", index=False)

