from inspect import formatannotation
import os
from bs4 import BeautifulSoup
import re

# For Windows (relative path) 
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'debugTable_case3.html')

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

# Get header row to count number of columns in table
headerRow = removeNewLines(allRows[0].contents)
numberOfColumns = len(headerRow)

tableRepr = []

rowSpans = []

# Step 1 : Check for rowspans and store their positions in dict
for rowIndex, row in enumerate(allRows):
    rowChildren = row.contents
    # Remove \n char in children list
    cleanRowChildren = removeNewLines(rowChildren)
    # Check for rowspan attribute
    for colIndex, el in enumerate(cleanRowChildren):
        if el.get('rowspan') != None:
            valDict = {
                'col' : colIndex,
                'row' : rowIndex,
                'tagTxt' : el.text,
                'rowspans' : el.get('rowspan')
            }
            rowSpans.append(valDict)

# === INIT === #
# To store eventual rowspans in contained <tr>
rowspanList = []
# To store dictionnary keys (table titles)
headerTitles = []

# Go through <tr>
for rowIndex, row in enumerate(allRows):
    # To store values extracted
    resDict = {}
    # Extract row children
    rowChildren = row.contents
    # Remove \n char in children list
    cleanRowChildren = removeNewLines(rowChildren)
    # How many elements are in <tr>
    nbOfElements = len(cleanRowChildren)
    # Is there any rowspan ? If yes, which elements ?
    for colIndex, el in enumerate(cleanRowChildren):
        if el.get('rowspan') != None:
            rowspanDict = {
                'col' : colIndex,
                'row' : rowIndex,
                'tagTxt' : el.text,
                'rowspanNb' : el.get('rowspan')
            }
            # Store element with rowspans in dict in a list (for reference)
            rowspanList.append(rowspanDict)
    # If there's less elements in <tr>, then it's an indicator that cells have been merged !
    if len(cleanRowChildren) != numberOfColumns: 
        # Check where was element with rowspans and get their indexes (corr to columns)
        rowSpansIndexList = [rowspan['col'] for rowspan in rowspanList]
        # Create a reference index list of columns to compare it with rowSpansIndexList
        refIndexList = [i for i in range(numberOfColumns)]
        # Compare two lists to guess where to put <tr> orphans elements
        # Convert list to set (to do difference)
        rowSpansIndexSet = set(rowSpansIndexList)
        refIndexSet = set(refIndexList)
        # We have our orphans indexes !
        orphansIndex = list(refIndexSet.difference(rowSpansIndexSet))
        # Push orphan element in it's dict
        for orphan in orphansIndex:
            # First, insert missing elements in dict
            for i, missing in enumerate(rowSpansIndexList):
                dictOfRowspans = rowspanList[i]
                # Insert tagTxt data in missing elements
                resDict[headerTitles[missing]] = dictOfRowspans['tagTxt']
            # Second, insert orphan element in dict
            for elements in cleanRowChildren:
                cleanElement = elements.text.replace('\n', '')
                # Create result dictionnary with according title
                resDict[headerTitles[orphan]] = cleanElement
            # Push dict in table representation
            tableRepr.append(resDict)

    # No rowspans
    elif nbOfElements == numberOfColumns:
        # Is it first row ? All titles are here so extract them and create dict keys with them.
        if rowIndex == 0:
            for elements in cleanRowChildren:
                # Clean \n char and extract text from bs4 tag
                cleanElement = elements.text.replace('\n', '')
                # Push titles in header titles list (to create key of future dict)
                headerTitles.append(cleanElement)
                # == HERE -> Check if there's rowspans in title (for later)
        else:
            for index, elements in enumerate(cleanRowChildren):
                # Clean \n char and extract text from bs4 tag
                cleanElement = elements.text.replace('\n', '')
                # Create result dictionary with according title
                resDict[headerTitles[index]] = cleanElement
            # Push dict in table representation
            tableRepr.append(resDict)
     
print(tableRepr)








# # For reference
# rowSpanLength = len(rowSpans)

# # Step 2 : Construct Table representation
# for columnIndex in range(numberOfColumns):
#     tmpColList = []
#     for rowIndex, row in enumerate(allRows):
#         #Extract row chilren
#         rowChildren = row.contents
#         # Remove \n char in children list
#         cleanRowChildren = removeNewLines(rowChildren)
#         # Check if there's missing elements in row (due to rowspan)
#         if len(cleanRowChildren) != numberOfColumns:
#             # Where are we ? How many rowspans ?
#             currentCol = columnIndex
#             currentRow = rowIndex
#             # Check current pos against rowspans found in step 1 to get value
#             for index, dict in enumerate(rowSpans):
#                 if dict['col'] == currentCol and dict['row'] == currentRow - 1:
#                     # There's a merged cell here, get value from rowSpans list
#                     tmpColList.append(dict['tagTxt'])
#                     # Then delete rowspan entry in list
#                     del rowSpans[index]
#                 elif dict['col'] != currentCol and dict['row'] == currentRow - 1:
#                     # Find index of cell and push in list
#                     element = cleanRowChildren[currentCol - rowSpanLength].text.replace('\n', '')
#                     tmpColList.append(element)
#                     print(currentCol - rowSpanLength)
#             # if len(rowSpans) == 0:
#             #     # There's no more rowspan to process                 
#             #     element = cleanRowChildren[currentCol - rowSpanLength].text.replace('\n', '')
#             #     tmpColList.append(element)
#         else:
#             # Extract element
#             element = cleanRowChildren[columnIndex].text.replace('\n', '')
#             tmpColList.append(element)            
#     tableRepr.append(tmpColList)
# print(tableRepr)






# # Hold values useful to indicate if there was a rowspan before
# indicator = {
#     'status' : False, 
#     'value' : ''
# }

# for row in allRows:
#     # Extract row chilren
#     rowChildren = row.contents
#     # Remove \n char in children list
#     cleanRowChildren = removeNewLines(rowChildren)
#     # If last loop tour found a rowspan
#     if indicator['status'] == True:
#         # Put same value as last loop tour (since there's a rowspan, it's the same value)
#         column.append(indicator['value'])
#         # Reset indicator dict
#         indicator['status'] = False
#         indicator['value'] = ''
#     else:
#         # Check for rowspans
#         attributes = cleanRowChildren[0].attrs
#         if attributes.get('rowspan') != None:
#             column.append(cleanRowChildren[0].text.replace('\n', ''))
#             # Indicate that there's a rowspan for next loop & store value
#             indicator['status'] = True
#             indicator['value'] = cleanRowChildren[0].text.replace('\n', '')
#         else:
#             column.append(cleanRowChildren[0].text.replace('\n', ''))
# # Append column to table        
# tableRepr.append(column)
# print(tableRepr)