'''
Scrape wikipedia for band infos.

Link Format : https://en.wikipedia.org/wiki/<band_Name>
'''

import requests
from bs4 import BeautifulSoup
import itertools
import re

# ===================================== #
# =============== UTILS =============== #
# ===================================== #
def disambiguate(url):
    '''
        Function used to disambiguate url. For instance 'Nirvana' could mean buddhist concept of heaven 
        or the american band. In this case wikipedia redirects to link https://en.wikipedia.org/wiki/Nirvana_(disambiguation)
        for user to choose the exact searched term. 
        
        If there is an ambiguity, Wikipedia will refer ro band's page url like this : 
        https://en.wikipedia.org/wiki/Nirvana_(band)

        Or if there's another band elsewhere named the same (to do !!!) :
        https://en.wikipedia.org/wiki/Nirvana_(British_band)

        @params     {str}       URL to query
        @returns    {object}    Response 
    '''
    # Test URL
    response = requests.get(url)
    if response.status_code == 404:
        newURL = url.replace('_(band)', '')
        return requests.get(newURL)
    elif response.status_code == 200:
        return response
        

def getBandCard(response):
    soup = BeautifulSoup(response.content, "html.parser")
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
    
    return infosDict


# ==================================== #
# =============== MAIN =============== #
# ==================================== #
bandName = "Knocked Loose"
format = bandName.replace(' ', '_')
query = format + "_(band)" # For disambiguation (may also refer to other things)
URL = f"https://en.wikipedia.org/wiki/{query}"

resp = disambiguate(URL)

if resp.status_code == 200:
    print(getBandCard(resp))

elif resp.status_code == 404:
    print("No wikipedia for this band")