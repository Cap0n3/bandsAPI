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

# Get header row (with titles) to count number of columns in table
headerRow = removeNewLines(allRows[0].contents)
numberOfColumns = len(headerRow)

tableRepr = []

# insert header titles in new lists
for title in headerRow:
    tmpList = [title.text]
    tableRepr.append(tmpList)


for rowIndex, row in enumerate(allRows):
    rowChildren = row.contents
    # Remove \n char in children list
    cleanRowChildren = removeNewLines(rowChildren)
    # Always skip titles row
    if rowIndex != 0:
        # Go through elements in row
        for colIndex, element in enumerate(cleanRowChildren):
            # Check for rowspan attribute in row elements
            if element.get('rowspan') != None:
                # Get number of rowspans
                rowspanNumber = element.get('rowspan')
                # Check if it's first row (TO ADAPT LATER)
                if rowIndex == 1:
                    # Insert element in list x times according to rowspan
                    for spans in range(int(rowspanNumber)):
                        cleanElement = element.text.replace('\n', '')
                        tableRepr[colIndex].append(cleanElement)
            # If there's no rowspan
            elif element.get('rowspan') == None:
                # Check if a spot is available somewhere in lists at current row
                for index in range(numberOfColumns):
                    # Check if index exists, if not then put element in list free spot and break
                    if not 0 <= index < len(tableRepr[colIndex]):
                        cleanElement = element.text.replace('\n', '')
                        tableRepr[colIndex].append(cleanElement)
                        break

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