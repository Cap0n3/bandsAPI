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
def formatTagToText(tag):
    ''' TO RE-EVALUTATE !!!! Keep for span removal but nothing else ?

    This func converts bs4 tags to readable text, get rid of
    hidden spans and format text if any weird characters is found.
    
    Parameters
    ----------
    tag : bs4.element.Tag
        Tags to clean and convert
    
    Returns
    -------
    string
        Cleaned text string

    '''
    # Get rid of span with style="display: none" (it there's one)
    if tag.span != None:
        attrValue = tag.span.get_attribute_list('style')
        if attrValue[0] != None and attrValue[0] == "display:none":
            tag.span.string = ""

    # Remove links (like [1][2] ...) from title
    cleanText = re.sub('\[\d+\]', '', tag.text)

    # Get rid of weird non-ascii chars
    cleanText = cleanText.replace('–', '-')

    return cleanText

def disambiguate(url):
    '''
    Function used to disambiguate url. For instance 'Nirvana' could mean buddhist concept of heaven 
    or the american band. In this case wikipedia redirects to link https://en.wikipedia.org/wiki/Nirvana_(disambiguation)
    for user to choose the exact searched term. 
    
    If there is an ambiguity, Wikipedia will refer ro band's page url like this : 
    https://en.wikipedia.org/wiki/Nirvana_(band)

    Or if there's another band elsewhere named the same (to do !!!) :
    https://en.wikipedia.org/wiki/Nirvana_(British_band)

    Parameters
    ----------
    string     
        URL to query
    
    Returns
    ------- 
    class requests.models.Response
        HTTP Response 
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
    
    Parameters
    ----------
    soup : class bs4.BeautifulSoup
        Page's soup
    
    Returns
    -------
    Dict
        Dictionnary containing all infos
    '''

    # Get Info box table on the right
    infoBoxTable = soup.find(class_="infobox vcard plainlist")
    
    tableRows = infoBoxTable.find_all("tr")
    
    headCellsList = [row.th for row in tableRows]
    cellsList = [row.td for row in tableRows]
    resultDict = {}

    # ====== Infos extraction ====== #
    # Lambda Func to clean text from links like [3] or [23]
    cleanText = lambda strToClean : re.sub('\[\d+\]', '', strToClean)

    for label, info in itertools.zip_longest(headCellsList, cellsList):
        # First extract titles <th> text
        title = label.text if label != None else "None"
        if title == "":
            title = "No Title"
        
        # Second, deal with content in <td>
        content = ""
        if info != None:
            unorderedList = info.ul
            # It's just text, no <ul>
            if unorderedList == None:
                content = cleanText(info.text)
                resultDict[title] = content
            else:
                # It's <ul> so extract list elements
                elementList = []
                listEl = unorderedList.find_all("li")
                for el in listEl:
                    elementList.append(cleanText(el.text))
                resultDict[title] = elementList
    
    # Filter out entry with "None" key (Probalbly image in card)
    if "None" in resultDict:
        resultDict.pop("None")
    
    return resultDict

def getUlDiscography(soup):
    '''
    This func scraps 'Discography' section in wikipeda, more specificly it scaps all <ul> tags 
    in between heading "Discography" (<h2>) and next heading <h2>. Often discography 
    is contained in an unordered list but it's not always the case.

    Parameters
    ----------
    soup : class bs4.BeautifulSoup
        Page's beautiful soup.
    
    Returns
    -------
    list
        Discography list
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
bandName = "Knocked Loose"
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
    prettyDict = json.dumps(mainBandDict, indent=4, ensure_ascii=False)
    print(prettyDict)
    
elif resp.status_code == 404:
    print("No wikipedia for this band, check spelling of band name.")