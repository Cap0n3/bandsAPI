import requests
from bs4 import BeautifulSoup
import itertools
import re
import json

class BandWiki:
    def __init__(self, bandName):
        self.bandName = bandName

    def formatTagToText(self, _tag):
        ''' TO RE-EVALUTATE !!!! Keep for span removal but nothing else ?

        This func converts bs4 tags to readable text, get rid of
        hidden spans and format text if any weird characters is found.
        
        Parameters
        ----------
        `tag` : `bs4.element.Tag`
            Tags to clean and convert.
        
        Returns
        -------
        `string`
            Cleaned text string.

        '''
        # Get rid of span with style="display: none" (it there's one)
        if _tag.span != None:
            attrValue = _tag.span.get_attribute_list('style')
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
        `_baseURL` : `string`    
            URL to query
        
        Returns
        -------
        `string`
            URL with no `_band` string inside.

        OR

        `class requests.models.Response`
            HTTP Response.
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

    @staticmethod    
    def getBandCard(_soup):
        '''
        This funcs extract wiki card (left side of page) with essential infos of band.
        
        Parameters
        ----------
        `_soup` : `class bs4.BeautifulSoup`
            Page's soup.
        
        Returns
        -------
        `Dict`
            Dictionnary containing all infos.
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

    @staticmethod
    def extractTable(table):
        '''
        This method extract informations contained in html tables and convert it to dictionnaries
        with keys corresponding to table titles row. Each dictionnary value represent a row of the
        table.

        Note : This method is a dependency of `getDiscography()`
        
        Parameters
        ----------
        `table` : `<class 'bs4.element.Tag'>`
            BS4 table tag.

        Returns
        -------
        `List`
            List with dictionnaries inside.
        '''
        def removeNewLines(lst):
            '''
            This function return a filtered list cleaned of new line chars.

            Params
            ------
            lst : list
                list to filter
            
            Returns
            -------
            list
                filtered list
            '''
            return list(filter(lambda x: False if x == "\n" else True, lst))
        
        allRows = table.find_all("tr")

        # Get header row (with titles) to count number of columns in table
        headerRow = removeNewLines(allRows[0].contents)
        tableRepr = []
        # Start of row infos (not the titles)
        rowStart = 1 

        # insert header titles in new lists
        for title in headerRow:
            tmpList = []
            # Check for rowspan attribute in title row
            if title.get('rowspan') != None:
                # Get number of rowspans
                rowspanNumber = title.get('rowspan')
                # Define offset
                rowStart = int(rowspanNumber)
                # Push title in list
                tmpList = [title.text.replace('\n', '')]
                tableRepr.append(tmpList)
            else:
                tmpList = [title.text.replace('\n', '')]
                tableRepr.append(tmpList)


        for rowIndex, row in enumerate(allRows):
            '''
            If there's rowspans in header cells (titles) there'll be an offset in table representation rows.
            Note : Offset is used as index below to populate lists in tableRepr, it shoud start at one and then increment.
            '''
            rowOffset = rowIndex - (rowStart - 1)
            # Get content of row
            rowChildren = row.contents
            # Remove \n char in children list
            cleanRowChildren = removeNewLines(rowChildren)
            # === PREPARE FIRST ROW OF LIST === #
            if rowIndex == rowStart:
                # 1. First, go through elements in row and find rowspans
                for colIndex, element in enumerate(cleanRowChildren):
                    # Check for rowspan attribute in row elements
                    if element.get('rowspan') != None:
                        # Get number of rowspans
                        rowspanNumber = element.get('rowspan')
                        # Clean element
                        cleanElement = element.text.replace('\n', '')
                        # If first row, simply insert element in column index
                        if rowIndex == rowStart:
                            # Insert element in list x times according to rowspan
                            for spans in range(int(rowspanNumber)):
                                tableRepr[colIndex].append(cleanElement)
                
                # 2. Second, find elements in row with no rowspans
                for element in cleanRowChildren:
                    if element.get('rowspan') == None:
                        # Clean element
                        cleanElement = element.text.replace('\n', '')
                        # Check if a spot is available somewhere in lists at current row
                        for colList in tableRepr:
                            try:
                                # Check if index exists
                                colList[rowOffset]
                            except IndexError:
                                # If not then spot is available for element
                                colList.insert(rowOffset, cleanElement)
                                # Spot has been found, break loop
                                break
                            else:
                                # Continue searching a spot in lists
                                continue

            # === CONTINUE TO FILL ROWS IN LIST === #
            elif rowIndex > rowStart:
                for element in cleanRowChildren:
                    cleanElement = element.text.replace('\n', '')
                    if element.get('rowspan') != None:
                        for colList in tableRepr:
                            try:
                                # Check if index exists
                                colList[rowOffset]
                            except IndexError:
                                # If not then spot is available for element
                                # Get rowspan numbers
                                rowspanNumber = int(element.get('rowspan'))
                                # Insert element in list x times according to rowspan
                                for spans in range(int(rowspanNumber)):
                                    colList.insert(rowOffset + rowspanNumber, cleanElement)
                                # Spot has been found, break loop
                                break
                            else:
                                # Continue searching a spot in lists
                                continue
                    # If no rowspans
                    if element.get('rowspan') == None:
                        for colList in tableRepr:
                            try:
                                # Check if index exists
                                colList[rowOffset]
                            except IndexError:
                                # If not then spot is available for element
                                colList.insert(rowOffset, cleanElement)
                                # Spot has been found, break loop
                                break
                            else:
                                # Continue searching a spot in lists
                                continue
        
        # === CONVERT LISTS RESULTS TO JSON DICT === #
        titles = [lst[0] for lst in tableRepr]
        colLen = len(tableRepr[0])

        finalResList = []

        for i in range(colLen):
            if i != 0:
                tmpDict = {}
                # Extract row data
                for title, lst in enumerate(tableRepr):
                    dictKey = titles[title]
                    dictVal = lst[i]
                    tmpDict[dictKey] = dictVal
                finalResList.append(tmpDict)
        
        return finalResList

    def getDiscography(self, _soup):
        '''
        This func scraps 'Discography' section in wikipeda, more specificly it scaps all `<ul>`
        and `<table>` tags in between heading "Discography" `<h2>` and next heading `<h2>`. Often discography 
        is contained in an unordered list but it's not always the case.

        Parameters
        ----------
        `_soup` : `class bs4.BeautifulSoup`
            Page's beautiful soup.
        
        Returns
        -------
        `list`
            Discography list
        '''
        # Utils
        removeLinks = lambda txt : re.sub('\[\d+\]', '', txt)

        def ulToDict(_albums):
            listOfdict = []
            for album in _albums:
                resDict = {}
                cleanedText = removeLinks(album.text)
                # Extract year from string (in paranthesis)
                yearRes = re.findall(r"(\(\d{4}\))", cleanedText)
                # remove parantesis from result
                albumYear = re.sub(r"(\(|\))", "", yearRes[0])
                # Remove (<year>) from text
                albumName = re.sub(r"(\(\d{4}\))", "", cleanedText)
                # Populate dict & append to list
                resDict["Name"] = albumName
                resDict["Year"] = albumYear
                listOfdict.append(resDict)
            return listOfdict
        
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
                    albumsDict = ulToDict(albums)
                    for album in albumsDict:
                        discography.append(album)
                # Sometimes <ul> is wrapped in a div
                elif tagName == "div":
                    albums = node.find_all("li")
                    albumsDict = ulToDict(albums)
                    for album in albumsDict:
                        discography.append(album)
                # Sometimes it's a <table>
                elif tagName == "table":
                    albumList = self.extractTable(node)
                    # To avoid getting list in a list
                    for album in albumList:
                        discography.append(album)
            
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
        `Dict`
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
            bandDiscography = self.getDiscography(soup)
            
            # Add discography to main result dictionnary
            mainResultDict["Discography"] = bandDiscography
            
            return mainResultDict
            
        elif resp.status_code == 404:
            raise AttributeError("No wikipedia for this band, check spelling of band name.")