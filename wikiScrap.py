'''
Scrape wikipedia for band infos.

Link Format : https://en.wikipedia.org/wiki/<band_Name>
'''

import requests
from bs4 import BeautifulSoup
import itertools
import re

BAND = "Metallica" # Change name here
QUERY = BAND.replace(' ', '_')
URL = f"https://en.wikipedia.org/wiki/{QUERY}"

resp = requests.get(URL)

if resp.status_code == 200:
    soup = BeautifulSoup(resp.content, "html.parser")
    # Get Info box table on the right
    infoBoxTable = soup.find(class_="infobox vcard plainlist")
    
    # Get all title label
    infoLabels = infoBoxTable.find_all(class_="infobox-label")
    
    # Get all infos
    infos = infoBoxTable.find_all(class_="infobox-data")

    # === EXTRACT INFO FROM RIGHT TABLE === #
    infosDict = {}
    
    for label, info in itertools.zip_longest(infoLabels, infos):
        # Remove links (like [1][2] ...) from title 
        cleanText = re.sub('\[\d\]', '', info.text)
        
        # Place elements separated by new line in array
        if info.text.find("\n") >= 0:
            arr = cleanText.split("\n")
            # Remove empty element from array
            filteredArr = [el for el in arr if el!='']
            infosDict[label.text] = filteredArr
        else:
            infosDict[label.text] = cleanText
    
    print(infosDict)

elif resp.status_code == 404:
    print("No wikipedia for this band")