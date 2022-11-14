from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
import pandas as pd


def get_incident_data(nrows): # Add feature to get all rows
    # Setup of Webdriver and Selenium
    options = Options()
    #options.headless = True # Uncomment to run scraper in headless mode
    service = Service(executable_path="C:\Program Files (x86)\chromedriver.exe")
    driver = webdriver.Chrome(options=options, service=service)
    # Here we are populating the dataset by scraping each page's table.
    url = "https://www.cityofmadison.com/police/newsroom/incidentreports/"
    driver.get(url)
    data = []  
    
    while len(data) < nrows: 
        main_content = driver.find_element("id", "main-content")
        rows = main_content.find_elements("class name", "row.incident-reports")[1:] # Slicing off header row 
        for row in rows:
            date = row.find_element("class name", "date")
            incident = row.find_element("class name", "agency")
            casenumber = row.find_element("class name", "casenumber")
            address = row.find_element("class name", "address")
            officer = row.find_element("class name", "releasedby")
            updated = row.find_element("class name", "updated")
            link = row.find_element("tag name", "a")
            data.append([date.text, incident.text, address.text, officer.text, 
                         casenumber.text, updated.text, link.get_attribute("href")])
        try:
            next_button = main_content.find_element("link text", "Next »")
            next_button.click()
        except NoSuchElementException:
            break
            
    # Converting data to a pandas Dataframe
    df = pd.DataFrame(data, columns=["date", "incident","address","officer","casenumber","updated","link"])
    # Filling description column in dataset
    description_list = []
    for link in df["link"]:
        driver.get(link)
        description = driver.find_elements("class name", "span5")[-1]
        description_list.append(description.text)
    df["description"] = description_list
    
    driver.quit()
    return(df)
