from inspect import formatannotation
import os
from bs4 import BeautifulSoup
import re

# For Windows (relative path) 
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'debugTable_case0.html')

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
numberOfColumns = len(headerRow)

tableRepr = []

# insert header titles in new lists
for title in headerRow:
    tmpList = [title.text.replace('\n', '')]
    tableRepr.append(tmpList)


for rowIndex, row in enumerate(allRows):
    rowChildren = row.contents
    # Remove \n char in children list
    cleanRowChildren = removeNewLines(rowChildren)
    # === PREPARE FIRST ROW OF LIST === #
    if rowIndex == 1:
        # 1. First, go through elements in row and find rowspans
        for colIndex, element in enumerate(cleanRowChildren):
            # Check for rowspan attribute in row elements
            if element.get('rowspan') != None:
                # Get number of rowspans
                rowspanNumber = element.get('rowspan')
                # Clean element
                cleanElement = element.text.replace('\n', '')
                # If first row, simply insert element in column index
                if rowIndex == 1:
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
                        colList[rowIndex]
                    except IndexError:
                        # If not then spot is available for element
                        colList.insert(rowIndex, cleanElement)
                        # Spot has been found, break loop
                        break
                    else:
                        # Continue searching a spot in lists
                        continue
    
    # === CONTINUE TO FILL ROWS IN LIST === #
    elif rowIndex > 1:
        for element in cleanRowChildren:
            cleanElement = element.text.replace('\n', '')
            if element.get('rowspan') != None:
                for colList in tableRepr:
                    try:
                        # Check if index exists
                        colList[rowIndex]
                    except IndexError:
                        # If not then spot is available for element
                        # Get rowspan numbers
                        rowspanNumber = int(element.get('rowspan'))
                        # Insert element in list x times according to rowspan
                        for spans in range(int(rowspanNumber)):
                            colList.insert(rowIndex + rowspanNumber, cleanElement)
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
                        colList[rowIndex]
                    except IndexError:
                        # If not then spot is available for element
                        colList.insert(rowIndex, cleanElement)
                        # Spot has been found, break loop
                        break
                    else:
                        # Continue searching a spot in lists
                        continue
        # For debugging
        # if rowIndex == 3:
        #     break

print(tableRepr)


















# rowSpans = []

# # Step 1 : Check for rowspans and store their positions in dict
# for rowIndex, row in enumerate(allRows):
#     rowChildren = row.contents
#     # Remove \n char in children list
#     cleanRowChildren = removeNewLines(rowChildren)
#     # Check for rowspan attribute
#     for colIndex, el in enumerate(cleanRowChildren):
#         if el.get('rowspan') != None:
#             valDict = {
#                 'col' : colIndex,
#                 'row' : rowIndex,
#                 'tagTxt' : el.text,
#                 'rowspans' : el.get('rowspan')
#             }
#             rowSpans.append(valDict)

# # === INIT === #
# # To store eventual rowspans in contained <tr>
# rowspanList = []
# # To store dictionnary keys (table titles)
# headerTitles = []

# # Go through <tr>
# for rowIndex, row in enumerate(allRows):
#     # To store values extracted
#     resDict = {}
#     # Extract row children
#     rowChildren = row.contents
#     # Remove \n char in children list
#     cleanRowChildren = removeNewLines(rowChildren)
#     # How many elements are in <tr>
#     nbOfElements = len(cleanRowChildren)
#     # Is there any rowspan ? If yes, get infos (pos, content, rowspans) in dict
#     for colIndex, el in enumerate(cleanRowChildren):
#         if el.get('rowspan') != None:
#             rowspanDict = {
#                 'col' : colIndex,
#                 'row' : rowIndex,
#                 'tagTxt' : el.text,
#                 'rowspanNb' : el.get('rowspan')
#             }
#             # Store element with rowspans in dict in a list (for reference)
#             rowspanList.append(rowspanDict)
#     # If there's less elements in <tr>, then it's an indicator that cells have been merged !
#     if len(cleanRowChildren) != numberOfColumns: 
#         # Check where was element with rowspans in previous row and get their column indexes
#         rowSpansIndexList = [rowspan['col'] for rowspan in rowspanList if rowspan['row'] == rowIndex - 1]
#         # Create a reference index list of columns to compare it with rowSpansIndexList
#         refIndexList = [i for i in range(numberOfColumns)]
#         # Compare two lists to guess where to put <tr> "orphans" elements
#         # Convert list to set (to do group difference)
#         rowSpansIndexSet = set(rowSpansIndexList)
#         refIndexSet = set(refIndexList)
#         # Ok, we have our orphans column indexes !
#         orphansIndex = list(refIndexSet.difference(rowSpansIndexSet))
#         print("Orphan Index : "  + str(orphansIndex))
#         # Push orphan element in it's dict
#         for index, orphan in enumerate(orphansIndex):
#             # First, insert missing elements in dict
#             for i, missing in enumerate(rowSpansIndexList):
#                 dictOfRowspans = rowspanList[i]
#                 # Insert tagTxt data in missing elements
#                 resDict[headerTitles[missing]] = dictOfRowspans['tagTxt']
#             # Second, insert orphan element in dict
#             element = cleanRowChildren[index]
#             cleanElement = element.text.replace('\n', '')
#             resDict[headerTitles[orphan]] = cleanElement
#         # Push dict in table representation
#         tableRepr.append(resDict)

#     # No rowspans
#     elif nbOfElements == numberOfColumns:
#         # Is it first row ? All titles are here so extract them and create dict keys with them.
#         if rowIndex == 0:
#             for elements in cleanRowChildren:
#                 # Clean \n char and extract text from bs4 tag
#                 cleanElement = elements.text.replace('\n', '')
#                 # Push titles in header titles list (to create key of future dict)
#                 headerTitles.append(cleanElement)
#                 # == HERE -> Check if there's rowspans in title (for later)
#         else:
#             for index, elements in enumerate(cleanRowChildren):
#                 # Clean \n char and extract text from bs4 tag
#                 cleanElement = elements.text.replace('\n', '')
#                 # Create result dictionary with according title
#                 resDict[headerTitles[index]] = cleanElement
#             # Push dict in table representation
#             tableRepr.append(resDict)

# print(rowspanList)  
# print(tableRepr)