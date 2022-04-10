import requests
from bs4 import BeautifulSoup
import itertools
import re

class BandWiki:
    def __init__(self, bandName):
        self.bandName = bandName

    def formatTagToText(self, _tag):
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
        if _tag.span != None:
            attrValue = tag.span.get_attribute_list('style')
            if attrValue[0] != None and attrValue[0] == "display:none":
                _tag.span.string = ""

        # # Remove links (like [1][2] ...) from title
        # cleanText = re.sub('\[\d+\]', '', _tag.text)

        # # Get rid of weird non-ascii chars
        # cleanText = cleanText.replace('–', '-')

        return _tag.text

    def disambiguate(self, _baseURL):
        '''
        Function used to disambiguate url. For instance 'Nirvana' could mean buddhist concept of heaven 
        or the american band. In this case wikipedia redirects to link https://en.wikipedia.org/wiki/Nirvana_(disambiguation)
        for user to choose the exact searched term. 
        
        If there is an ambiguity, Wikipedia will refer to band's page url like this : 
        https://en.wikipedia.org/wiki/Nirvana_(band)

        Or if there's another band elsewhere with the same name (to do !!!) :
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
        # Format URL
        format = self.bandName.replace(' ', '_')
        query = format + "_(band)" # For disambiguation (may also refer to other things)
        URL = _baseURL + query

        # Test URL
        response = requests.get(URL)
        if response.status_code == 404:
            newURL = URL.replace('_(band)', '')
            return requests.get(newURL)
        elif response.status_code == 200:
            return response
            
    def getBandCard(self, _soup):
        '''
        This funcs extract wiki card (left side of page) with essential infos of band.
        
        Parameters
        ----------
        _soup : class bs4.BeautifulSoup
            Page's soup
        
        Returns
        -------
        Dict
            Dictionnary containing all infos
        '''

        # Get Info box table on the right
        infoBoxTable = _soup.find(class_="infobox vcard plainlist")
        
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

    def getUlDiscography(self, _soup):
        '''
        This func scraps 'Discography' section in wikipeda, more specificly it scaps all <ul> tags 
        in between heading "Discography" (<h2>) and next heading <h2>. Often discography 
        is contained in an unordered list but it's not always the case.

        Parameters
        ----------
        _soup : class bs4.BeautifulSoup
            Page's beautiful soup.
        
        Returns
        -------
        list
            Discography list
        '''
        # Utils
        removeLinks = lambda txt : re.sub('\[\d+\]', '', txt)

        # Navigate DOM (to find everything below Discography)
        try:
            discoSpan = _soup.find_all("span", id="Discography")
            if len(discoSpan) == 0:
                raise NameError
        except NameError:
            print(f"ERROR : No span with id='Discography' was found for '{self.bandName}' !")
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
                        cleanedText = removeLinks(album.text)
                        discography.append(cleanedText)
                # Sometimes <ul> is wrapped in a div
                elif tagName == "div":
                    albums = node.find_all("li")
                    for album in albums:
                        cleanedText = removeLinks(album.text)
                        discography.append(cleanedText)
                # Sometimes it's a table
                elif tagName == "table":
                    rows = node.find_all("tr")
                    # Extract all first columns titles (first row)
                    columnTitles = rows[0].contents
                    # Remove possible \n in column element
                    columnTitles = list(filter(lambda x: False if x == "\n" else True, columnTitles))
                    
                    # Find where is "Title" column and find its index
                    for title in enumerate(columnTitles):
                        # Remove residual \n in text
                        cleanedTitle = title[1].text.replace('\n', '')
                        # Get index of column
                        if cleanedTitle == "Title":
                            columnIndex = title[0]
                    
                    # Loop through title column and get results
                    albumList = []
                    for index, row in enumerate(rows, 0):
                        elList = row.contents
                        filtered_elList = list(filter(lambda x: False if x == "\n" else True, elList))
                        # Skip first row (where word "Title" is)
                        if index != 0:
                            albumName = filtered_elList[columnIndex].text.replace('\n', '')
                            albumList.append(removeLinks(albumName))

                    # HERE - Works with Graveyard but not Melvins ...
                    print(albumList)
                        
                    # Iterate array and skip first row (to skip title)
                    # for el in newRowArray:
                    #     if el[0] == 0:
                    #         pass
                    #     else:
                    #         print(el[1].text)
                    
                    # Get "Title" column
                    # for row in rows:
                    #     elList = row.contents
                    #     filtered_elList = list(filter(lambda x: False if x == "\n" else True, elList))
                    #     print(filtered_elList[columnIndex].text.replace('\n', ''))

                    # for title in filtered_elList:
                    #     print(title)

                    # for row in rows:
                    #     elList = row.contents
                    #     filtered_elList = list(filter(lambda x: False if x == "\n" else True, elList))
                    #     print(filtered_elList[0].text)
                    # newRowArray = []
                    # Create new array with index (to skip first row of table)
                    # for row in enumerate(rows):
                    #     newRowArray.append(row)
                    # # Iterate array and skip first row (to skip title)
                    # for el in newRowArray:
                    #     if el[0] == 0:
                    #         pass
                    #     else:
                    #         print(el[1].text)
                    

            # Check of section is correctly formatted.
            if len(discography) == 0:
                print(f"ERROR : It seems that section 'Discography' is formatted differently for '{self.bandName}' band page, could be a table instead of <ul> ?")
                return None
            else:
                return discography

    def getAllInfos(self):
        '''
        This method is the main method of class BandWiki, it'll call necessary methods to construct final infos 
        for bands by merging differents dictionnaries returned by these methods.

        It also call BeautifulSoup to scrap wikipedia and handle response status if something goes wrong.

        Returns
        -------
        Dict
            Main dictionnary with all relevant infos scrapped of wikipedia 
        '''
        
        # format = self.bandName.replace(' ', '_')
        # query = format + "_(band)" # For disambiguation (may also refer to other things)
        # URL = f"https://en.wikipedia.org/wiki/{query}"
        
        # WORKING HERE
        baseURL = "https://en.wikipedia.org/wiki/"

        resp = self.disambiguate(baseURL)

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, "html.parser")
            mainResultDict = self.getBandCard(soup)
            bandDiscography = self.getUlDiscography(soup)
            
            # Add discography to main result dictionnary
            mainResultDict["Discography"] = bandDiscography
            
            return mainResultDict
            
        elif resp.status_code == 404:
            raise AttributeError("No wikipedia for this band, check spelling of band name.")