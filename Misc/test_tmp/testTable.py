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

# Get header row to count number of columns
headerRow = removeNewLines(allRows[0].contents)
numberOfColumns = len(headerRow)

tableRepr = []
column = []

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

# Step 2 : Construct Table representation
for columnIndex in range(numberOfColumns):
    tmpColList = []
    for rowIndex, row in enumerate(allRows):
        #Extract row chilren
        rowChildren = row.contents
        # Remove \n char in children list
        cleanRowChildren = removeNewLines(rowChildren)
        # Check if there's missing elements in row (due to rowspan)
        if len(cleanRowChildren) != numberOfColumns:
            # Where are we ? How many rowspans ?
            currentCol = columnIndex
            currentRow = rowIndex
            rowSpanLength = len(rowSpans)
            # Check current pos against rowspans found in step 1 to get value
            for index, dict in enumerate(rowSpans):
                if dict['col'] == currentCol and dict['row'] == currentRow - 1:
                    # There's a merged cell here
                    tmpColList.append(dict['tagTxt'])
                    # Delete rowspan entry in list
                    del rowSpans[index]
                elif dict['col'] != currentCol and dict['row'] == currentRow - 1:
                    # Find index of cell and push in list
                    element = cleanRowChildren[currentCol - rowSpanLength].text.replace('\n', '')
                    tmpColList.append(element)
                    print(currentCol - rowSpanLength)
        else:
            # Extract element
            element = cleanRowChildren[columnIndex].text.replace('\n', '')
            tmpColList.append(element)            
    tableRepr.append(tmpColList)
print(tableRepr)






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