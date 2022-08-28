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
from collections import namedtuple
import json
import re

# For Windows (relative path) 
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'tableHeader_case2.html')

# Logging init
logging.basicConfig(level=logging.NOTSET)
logger = logging.getLogger(__name__)

# ===================================== #
# ========= UTILITY FUNCTIONS ========= #
# ===================================== #

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

def scanRow(rowData):
    '''
    This function scan any given row and return informations about each cells. These infos are :
    - Cell column index 
    - Rowspan 
    - Colspan

    Params
    ------
    lst : list
        list of row content like [<th rowspan="2">Year</th>, <th rowspan="2">Album</th>].
    
    Returns
    -------
    list
        List of named tuples.
    '''
    resTable = []
    print(rowData)
    CellScan = namedtuple('CellScan', ['cellIndex', 'rowspan', 'colspan'])
    for colIndex, cell in enumerate(rowData):
        if cell.get('rowspan') != None:
            rowspan = int(cell.get('rowspan'))
            if cell.get('colspan'):
                colspan = int(cell.get('colspan'))
            else:
                colspan = 0
            cellScan = CellScan(colIndex, rowspan, colspan)
            resTable.append(cellScan)
        else:
            cellScan = CellScan(colIndex, 0, 0)
            resTable.append(cellScan)
    return resTable

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
    This function role is to determine table type and give some useful infos about table. 
    Type can be either simple or multidimensional.
    
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
    `tuple[str, int, int]`
        Tuple with either "simple" or "multidimensional" string, header length (number of header rows) and total columns in table.
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
        # Store number of columns of table (to return)
        if rowIndex == 0 : 
            totalColumns = contentCount
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
        return ("simple", totalHeaderRows, totalColumns)
    elif totalHeaderRows > 0 and titledRow > 0:
        return ("multidimensional", totalHeaderRows, totalColumns)
    else:
        logger.warning(f'Table type is unknown !')
        raise TypeError("Table type is unknown !")

tableType, headerRowLength, totalTableColumns = getTableType(allRows)

# ========= [STEP 3] - Get table header data in a list ========= #
'''
This step is important :
    1. Get first row and take care of rowspan & colspan TO create table list representation
    2. Start filling tableRepr with other rows
'''
tableRepr = []
headerFirstRow = removeNewLines(allRows[0].contents)

# 1. Get data of first row and create table list reprentation
for cell in headerFirstRow:
    columnReprList = []
    # Check for rowspan attribute in cell
    if cell.get('rowspan') != None:
        # Get number of rowspans of cell
        cellRowspan = int(cell.get('rowspan'))
        # Insert element n times in column list representation according to rowspan
        for i in range(cellRowspan):
            columnReprList.append(cell.text)
        # Push column list in table representation
        tableRepr.append(columnReprList)
    else:
        columnReprList = [cell.text.replace('\n', '')]
        tableRepr.append(columnReprList)

# Log result so far
logger.debug(f"\nTABLE FIRST ROW :\n{tableRepr}")

# Header have multiple cells
if headerRowLength > 1:
    # 2. Then that first row is done, insert other row of header (Skip first row (already done))
    for rowIndex, row in enumerate(allRows[1:]):
        # Since we skipped first element, row index is out whack so re-adjust rowIndex at correct index
        rowIndex += 1
        logger.debug(f"ROW INDEX : {rowIndex}")
        # Stop at end of table header
        #if rowIndex == headerRowLength: break
        # Get row content and clean them
        rowChildren = removeNewLines(row.contents)
        # Loop through elements and insert them in table list representation
        for cell in rowChildren:
            # Case 1 - Normal cell with no rowspans
            if cell.get('rowspan') == None:
                # Check if a spot is available somewhere in column lists at current row
                for colList in tableRepr:
                    try:
                        # Check if index exists
                        colList[rowIndex]
                    except IndexError:
                        # If not then spot is available for element
                        colList.insert(rowIndex, cell.text)
                        # Spot has been found, break loop
                        break
                    else:
                        # Continue searching a spot in lists
                        continue
            # Case 2 - Cell with rowspans
            if cell.get('rowspan') != None:
                # Check if a spot is available somewhere in column lists at current row
                for colList in tableRepr:
                    try:
                        # Check if index exists
                        colList[rowIndex]
                    except IndexError:
                        # If not then spot is available for element
                        # Get rowspan numbers
                        rowspanNumber = int(cell.get('rowspan'))
                        # Insert element in list x times according to rowspan
                        for spans in range(rowspanNumber):
                            colList.insert(rowIndex + rowspanNumber, cell.text)
                        # Spot has been found, break loop
                        break
                    else:
                        # Continue searching a spot in lists
                        continue

logger.debug(f"\nTABLE FINAL RESULT :\n{tableRepr}")



# === CASE 2 === #
# The header have several rows, it can have rowspans and colspans
# elif headerLength > 1:
#     # There's rowspan in header
#     maxRowspans = headerLength
#     # 1. LOOP THROUGHT ROWS OF HEADER
#     for rowIndex, row in enumerate(allRows):
#         # Get out of loop if we're outside header
#         if rowIndex == headerLength:
#             break
#         # Get row content & clean it
#         rowChildren = removeNewLines(row.contents)
#         # 2. LOOP THROUGH CELLS IN ROW
#         for colIndex, cell in enumerate(rowChildren):
#             columnReprList = []
#             # OK, cell has a rowspan attribute
#             if cell.get('rowspan') != None:
#                 # Get exact value of rowspan
#                 cellRowspan = int(cell.get('rowspan'))
#                 # Insert element n times in column list representation according to rowspan
#                 for i in range(cellRowspan):
#                     columnReprList.append(cell.text)
#                 # Add column to table list reprentation
#                 tableRepr.append(columnReprList)
#             # OK, cell has no rowspan attribute
#             elif cell.get('rowspan') == None:
#                 # Simply insert element at right column index
#                 # First test if column list reprentation has already been created
#                 try:
#                     tableRepr[colIndex]
#                 except IndexError:
#                     # Nope column list should be created
#                     columnReprList.append(cell.text)
#                     # Add column to table list reprentation
#                     tableRepr.append(columnReprList)
#                 else:
#                     # Yep it already exists, simply insert cell content
#                     tableRepr[colIndex].append(cell.text)
                    
                        



# print(tableRepr)

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

