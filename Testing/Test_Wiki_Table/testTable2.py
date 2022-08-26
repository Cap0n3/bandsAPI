'''
This file is a test file for the extractTable() function. It'll test isolated tables 
in Test_Wiki_Table folder that provoque bugs in the function. 

> Important ! The code below main should be exactly like in BandWiki.py.

For now, every case was covered except for case 7.
'''

from inspect import formatannotation
import os
import logging
import sys
from bs4 import BeautifulSoup
import json
import re

# For Windows (relative path) 
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'debugTable_case1.html')

# Logging init
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger(__name__)

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

# ======================== #
# ========= MAIN ========= #
# ======================== #

# Open html file
with open(filename, 'r') as htmlTestFile:
    soup = BeautifulSoup(htmlTestFile, "html.parser")

# [STEP 1] - Get every rows in selected table (every <tr></tr>)
allRows = soup.find_all("tr")

# [STEP 2] - Get table titles cells, catch any rowspans in first row (define rowstart) & create table list representation
'''
1. Get header first row
2. Catch any rowspan 
    - If there's not, go directly to 3. 
    - Define rowStart to be equal to rowspans
    > Note : rowStart will represent how many <tr> there is before table body (where useful data are) is reached.
3. Place each cell content (table titles) as first element of a list contained in a nested list 
like this : [['Year'], ['Album'], ['Label']] (it's our table representation in a list form) 
'''
# Get very first row of table
headerRow = removeNewLines(allRows[0].contents)
# Initiate our table list reprentation
tableRepr = []
# Default start index of table row (where data are)
rowStart = 1 

# === First loop - Create header of table list === #
# Catch any rowspans & create table representation (nested list, see point 3.)
for title in headerRow:
    tmpList = []
    # Check for rowspan attribute in title row
    if title.get('rowspan') != None:
        # Get number of rowspans
        rowspanNumber = title.get('rowspan')
        # Redefine start index (the start of actual data in table)
        rowStart = int(rowspanNumber)
        # Push title in list
        tmpList = [title.text.replace('\n', '')]
        tableRepr.append(tmpList)
    else:
        # There's no rowspan for this cell
        tmpList = [title.text.replace('\n', '')]
        tableRepr.append(tmpList)

# Log result for header (DEBUG)
logger.debug(f'Created header of table :\n {tableRepr}\n')

for rowIndex, row in enumerate(allRows):
    '''
    rowOffset variable represents current row index of row in table list representation with any excess <tr> due to rowspans 
    in header substracted. It will be used later as index below to populate lists in tableRepr, it shoud 
    start at ONE (default value) and then increment.

    Note : rowOffset is not the same as rowIndex or rowStart ! Excess <tr> due to rowspans in header are substracted.
    For instance, if there was 2 rowspans in header (two <tr>), the first data row index rowIndex will start at 3 where rowOffset 
    will always start at 1 and then increment. rowOffset represents the row index in table list reprentation.
    '''
    # Represent current index of row in table list representation
    rowOffset = rowIndex - (rowStart - 1)
    # Get data of row
    rowChildren = row.contents
    # Remove \n char in children list
    cleanRowChildren = removeNewLines(rowChildren)
    # === [STEP 3] PREPARE FIRST ROW OF LIST === #
    if rowIndex == rowStart:
        # a. First, go through elements in row and find rowspans (if there's any)
        for colIndex, element in enumerate(cleanRowChildren):
            # Check for rowspan attribute in row elements
            if element.get('rowspan') != None:
                # Get number of rowspans
                rowspanNumber = element.get('rowspan')
                # Clean element
                cleanElement = element.text.replace('\n', '')
                # If first row, simply insert element in column index
                if rowIndex == rowStart:
                    # Insert element in table list representation x times according to rowspan
                    for spans in range(int(rowspanNumber)):
                        tableRepr[colIndex].append(cleanElement)
        
        # b. Second, find elements in row with NO rowspans (if there's any) and insert them where there's space
        for element in cleanRowChildren:
            if element.get('rowspan') == None:
                # Clean element
                cleanElement = element.text.replace('\n', '')
                # Check if a spot is available somewhere in table list representation columns (inner lists) at current row
                for colList in tableRepr:
                    try:
                        # Check if index exists
                        colList[rowOffset]
                    except IndexError:
                        # If index does not exists then a spot is available for this element
                        colList.insert(rowOffset, cleanElement)
                        # Spot has been found, break loop
                        break
                    else:
                        # Index already exists, ok continue searching for a spot in columns (lists)
                        continue
        
        # Log result for first row (DEBUG)
        logger.debug(f'Created first row of table :\n {tableRepr}\n')
    
    # === [STEP 4] CONTINUE TO FILL ROWS IN LIST === #
    elif rowIndex > rowStart:
        for element in cleanRowChildren:
            cleanElement = element.text.replace('\n', '')
            # a. If there's rowspans
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
            # b. If there's NO rowspans
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
    # For debugging
    # if rowIndex == 3:
    #     break

# === CONVERT LISTS RESULTS TO JSON DICT === #
# titles = [lst[0] for lst in tableRepr]
# colLen = len(tableRepr[0])

# resList = []

# for i in range(colLen):
#     if i != 0:
#         tmpDict = {}
#         # Extract row data
#         for title, lst in enumerate(tableRepr):
#             dictKey = titles[title]
#             dictVal = lst[i]
#             tmpDict[dictKey] = dictVal
#         #Convert dict to json
#         jsonDict = json.dumps(tmpDict, indent=4)
#         resList.append(jsonDict)
    
#print(resList[0])
#print(colLen)
logger.debug(f'Completed table list :\n {tableRepr}\n')