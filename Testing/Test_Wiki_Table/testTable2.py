from inspect import formatannotation
import os
from bs4 import BeautifulSoup
import json
import re

# For Windows (relative path) 
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'debugTable_case5.html')

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

# ========= MAIN ========= #
# Open html file
with open(filename, 'r') as htmlTestFile:
    soup = BeautifulSoup(htmlTestFile, "html.parser")

allRows = soup.find_all("tr")

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
print(tableRepr)