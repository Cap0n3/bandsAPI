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
        

def getBandCard(soup):
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


def getDiscography(soup):
    '''
    This func scraps discography section in wikipeda (if there's one). 
    It seems that wikipedia puts term "Discography" in <h2> and is followed 
    by an <ul> containing albums. (Not fully tested)

    Parameters:
        soup (object): soup of page.
    Returns:
        dict:discography
    '''
    
    # Navigate DOM (to find everything below Discography)
    try:
        discoSpan = soup.find_all("span", id="Discographyy")
        if len(discoSpan) == 0:
            raise NameError
    except NameError:
        print("ERROR : No span with id='Discography' was found !")
    else:
        discoTitle = discoSpan[0].find_parents("h2")
        allSiblings = discoTitle[0].find_next_siblings()
        # Filter tags
        for node in allSiblings:
            tagName = node.name
            if tagName == "h2":
                break
            elif tagName == "ul" or tagName == "li":
                print(node.text)

# ==================================== #
# =============== MAIN =============== #
# ==================================== #
bandName = "Metallica"
format = bandName.replace(' ', '_')
query = format + "_(band)" # For disambiguation (may also refer to other things)
URL = f"https://en.wikipedia.org/wiki/{query}"

resp = disambiguate(URL)

if resp.status_code == 200:
    soup = BeautifulSoup(resp.content, "html.parser")
    bandWikiCard = getBandCard(soup)
    bandDiscography = getDiscography(soup)

    print(bandDiscography)
    

elif resp.status_code == 404:
    print("No wikipedia for this band")