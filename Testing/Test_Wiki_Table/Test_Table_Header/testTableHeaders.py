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
filename = os.path.join(dirname, 'tableHeader_case2.html')

# Logging init
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger(__name__)

def closest(lst, K):    
    return lst[min(range(len(lst)), key = lambda i: abs(lst[i]-K))]

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

# ========= [STEP 1] - Get every rows in selected table (every <tr></tr>) ========= #
allRows = soup.find_all("tr")

# ========= [STEP 2] - Get type of table (simple or multidimensional ?) and number of header rows ========= #
def getTableType(_allRows):
    '''
    This function role is to determine table type. Type can be either simple or multidimensional.
    
    Here's a simple table:
    
    | Name | Age | Genre |
    |------|-----|-------|
    | Jack | 23  | Male  |

    Here's a multidimensional table (with header cells at the start of each row) :

    |        | Dog | Cat | Total |
    |--------|-----|-----|-------|
    | Male   | 30  |  10 |   40  |
    | Female | 40  |  35 |   75  |
    | Total  | 70  |  45 |   115 |

    Parameters
    ----------
    `_allRows` : `<class 'bs4.element.ResultSet'>`
        BS4 result set, look like this : [<tr><td>Year</td><td>Album</td><td>Label</td></tr>, etc...]
     
     Returns
    -------
    `tuple[str, int]`
        Tuple with either "simple" or "multidimensional" string and number of header rows.
    '''
    totalHeaderRows = 0 # Row with only <th>
    titledRow = 0 # Row with one <th> and then <td>

    # Go through 10 first rows to get type of table
    for rowIndex, row in enumerate(_allRows):
        thCells = 0
        tdCells = 0
        if rowIndex == 9:
            break
        # Get row contents
        rowContents = row.contents
        contentCount = len(removeNewLines(rowContents))
        # Count type cells in row
        for content in rowContents:
            if content.name == "th":
                thCells += 1
            elif content.name == "td":
                tdCells += 1
        if contentCount == thCells:
            # There's only <th> in row (it's a header)
            totalHeaderRows += 1
            logger.debug(f"Row {str(rowIndex)} - <th> count = {thCells}, <td> count = {tdCells} at  => it's a header row !")
        elif thCells == 1 and tdCells == (contentCount - 1):
            # There's one <th> and the rest are <td>, it's a multidimensional table
            titledRow += 1
            logger.debug(f"Row {str(rowIndex)} - <th> count = {thCells}, <td> count = {tdCells} at  => it's a titled row !")
    # Final condition to decide type of table
    if totalHeaderRows > 0 and titledRow == 0:
        return ("simple", totalHeaderRows)
    elif totalHeaderRows > 0 and titledRow > 0:
        return ("multidimensional", totalHeaderRows)
    else:
        logger.warning(f'Table type is unknown !')
        raise TypeError("Table type is unknown !")

tableType, rowStart = getTableType(allRows)

# ========= [STEP 3] - Get table header data in a list ========= #
tableHeader = []
# === CASE 1 === #
if rowStart == 1:
    # Then header has one row, simply get data in row and put it in list
    headerOneRow = removeNewLines(allRows[0].contents)
    for cell in headerOneRow:
        tmpList = []
        cellContent = cell.text.replace('\n', '') # Convert to text + remove new lines
        tmpList.append(cellContent)
        tableHeader.append(tmpList)
    logger.debug(f'One line header :\n{tableHeader}')
# === CASE 2 === #
elif rowStart > 1:
    # There's rowspan in header
    totalRowSpans = rowStart
    # Get first header row
    rowChildren = allRows[0].contents
    # Remove \n char in children list
    cleanRowChildren = removeNewLines(rowChildren)
    print(cleanRowChildren)
    # Loop through elements in FIRST row ==> HERE !!! ONLY NEED FIRST ROW
    for colIndex, cell in enumerate(cleanRowChildren):
        tmpList = []
        # Check for rowspan attribute in row elements
        if cell.get('rowspan') != None:
            cellRowspan = int(cell.get('rowspan'))
            if totalRowSpans == cellRowspan:
                # Cells with rowspans that are exactly the total of header rows takes all header height (& have one data)
                cellContent = cell.text.replace('\n', '') # Convert to text + remove new lines
                tmpList.append(cellContent)
                tableHeader.append(tmpList)
            elif totalRowSpans > cellRowspan:
                # These cells have rowspans but don't take all height so they have other cells below them
                pass
        if cell.get('rowspan') == None:
            # No rowspan in this cell
            # First get this (upper) cell
            upperCellContent = cell.text.replace('\n', '') # Convert to text + remove new lines
            # Then cells underneath
            underCellsContent = [] # To store content from cells underneath
            # Skip row 1 and go to following rows
            for rowIndex in range(1, totalRowSpans):
                # Get rows underneath first row
                contentRowList = removeNewLines(allRows[rowIndex].contents)
                # Get Number of elements in row
                lengthOfRow = len(contentRowList)
                # Convert length to a list of indexes
                indexRangeList = [*range(lengthOfRow)]
                # Find closest element index of column index (it's necessarly corresponding cell in following rows)
                closestIndex = closest(indexRangeList, colIndex)
                # Get element & clean it
                belowCellContent = contentRowList[closestIndex]
                cleanBelowCellContent = belowCellContent.text.replace('\n', '')
                # Add it to list (if there's several following rows)
                underCellsContent.append(cleanBelowCellContent)
            # Combine data from upper with below cell
            combinedData = f'{upperCellContent} ({underCellsContent})'
            tmpList.append(combinedData)
            tableHeader.append(tmpList)
                        



print(tableHeader)

# headerCellScan = []

# for colIndex, cell in enumerate(headerRow):
#     rowspanNumber = 0
#     colspanNumber = 0
#     if cell.get('rowspan') != None:
#         # Get number of rowspans
#         rowspanNumber = int(cell.get('rowspan'))
#     if cell.get('colspan') != None:
#         colspanNumber = int(cell.get('colspan'))
#     '''
#     Put tuple result in a list where index is column number for cell :
#     [(rowspans, colspan), (rowspans, colspan), (rowspans, colspan),]
#     ''' 
#     headerCellScan.append((rowspanNumber, colspanNumber))

# # [STEP 3] - Create dictionnary
# for value in headerCellScan:
#     # Colspans
#     if value[1] != 0:
#         pass

# '''
# Premisse :

# 1. Several <th> in the first few <tr> (rows) should indicate a table header
# 2. One <th> and several <td> would indicate a 
# '''

