'''
Scrape wikipedia for band infos.

Link Format : https://en.wikipedia.org/wiki/<band_Name>
'''

import requests
from bs4 import BeautifulSoup
import itertools
import re

bandName = "Knocked Loose"
query = bandName.replace(' ', '_')
URL = f"https://en.wikipedia.org/wiki/{query}"

resp = requests.get(URL)

if resp.status_code == 200:
    soup = BeautifulSoup(resp.content, "html.parser")
    # Get Info box table on the right
    infoBoxTable = soup.find(class_="infobox vcard plainlist")
    
    # Get all title label
    infoLabels = infoBoxTable.find_all(class_="infobox-label")
    
    # Get all infos
    infos = infoBoxTable.find_all(class_="infobox-data")

    # Dict that'll contain all infos
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
    #for info in infos:
    #    print(info)

elif resp.status_code == 404:
    print("No wikipedia for this band")