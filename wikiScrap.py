'''
Scrape wikipedia for band infos.

Link Format : https://en.wikipedia.org/wiki/<band_Name>
'''

import requests
from bs4 import BeautifulSoup
import itertools
import re
import json

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
    '''
    This funcs extract wiki card (left side of page) with essential infos of band.
    Parameters:
        soup (object) : page's soup
    Returns:
        Dict : Dictionnary containing all infos
    '''
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
        cleanText = re.sub('\[\d+\]', '', info.text)
        
        # Place elements separated by new line in array
        if info.text.find("\n") >= 0:
            arr = cleanText.split("\n")
            # Remove empty element from array
            filteredArr = [el for el in arr if el!='']
            infosDict[label.text] = filteredArr
        else:
            infosDict[label.text] = cleanText
    
    return infosDict


def getUlDiscography(soup):
    '''
    This func scraps 'Discography' section in wikipeda, more specificly it scaps all <ul> tags 
    in between heading "Discography" (<h2>) and next heading <h2>. Often discography 
    is contained in an unordered list but it's not always the case.

    Parameters:
        soup (object): soup of page.
    Returns:
        list:discography
    '''
    
    # Navigate DOM (to find everything below Discography)
    try:
        discoSpan = soup.find_all("span", id="Discography")
        if len(discoSpan) == 0:
            raise NameError
    except NameError:
        print("ERROR : No span with id='Discography' was found !")
    else:
        discoTitle = discoSpan[0].find_parents("h2")
        allSiblings = discoTitle[0].find_next_siblings()
        discography = []
        # Filter tags
        for node in allSiblings:
            tagName = node.name
            if tagName == "h2":
                break
            elif tagName == "ul":
                albums = node.find_all("li")
                for album in albums:
                    cleanedText = re.sub('\[\d+\]', '', album.text)
                    discography.append(cleanedText)

        # Check of section is correctly formatted.
        if len(discography) == 0:
            print("It seems that section 'Discography' is formatted differently, could be a table instaed of <ul> ?")
            return None
        else:
            return discography

# ==================================== #
# =============== MAIN =============== #
# ==================================== #

# Check Melvins for table instead of <ul> (in Discography)
bandName = "Queens of the stone age"
format = bandName.replace(' ', '_')
query = format + "_(band)" # For disambiguation (may also refer to other things)
URL = f"https://en.wikipedia.org/wiki/{query}"

resp = disambiguate(URL)

if resp.status_code == 200:
    soup = BeautifulSoup(resp.content, "html.parser")
    mainBandDict = getBandCard(soup)
    bandDiscography = getUlDiscography(soup)
    # Add discography to main band dictionnary
    mainBandDict["Discography"] = bandDiscography
    
    # Convert it to json (Check weird characters)
    prettyDict = json.dumps(mainBandDict, indent=4)
    print(prettyDict)
    
elif resp.status_code == 404:
    print("No wikipedia for this band, check spelling of band name.")