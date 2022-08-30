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

# ====== UNCOMMENT TO TEST HERE ====== #
# For Windows (relative path) 
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'Test_Table_Header/tableHeader_case6.html')
# Open html file
with open(filename, 'r') as htmlTestFile:
    soup = BeautifulSoup(htmlTestFile, "html.parser")
allRows = soup.find_all("tr")

# ====== Logging init ====== #
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

def getSpans(cell):
    '''
    This function returns number of rowspan or colspan from a given cell.

    Params
    ------
    cell : `<class 'bs4.element.Tag'>`
        BS4 cell from table (like `<th rowspan="2">Year</th>`).
    
    Returns
    -------
    tuple
        Tuple with rowspan and colspan (return None if there's no rowspan/colspan)
    '''
    rowspan = int(cell.get('rowspan')) if (cell.get('rowspan') != None) else None
    colspan = int(cell.get('colspan')) if (cell.get('colspan') != None) else None
    return (rowspan, colspan)

# ============================== #
# ========= MAIN FUNCS ========= #
# ============================== #

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
            # logger.debug(f"Row {str(rowIndex)} - <th> count = {thCells}, <td> count = {tdCells} at  => it's a header row !")
        elif thCells == 1 and tdCells == (contentCount - 1):
            # There's one <th> and the rest are <td>, it's a multidimensional table
            titledRow += 1
            # logger.debug(f"Row {str(rowIndex)} - <th> count = {thCells}, <td> count = {tdCells} at  => it's a titled row !")
    # Final condition to decide type of table
    if totalHeaderRows > 0 and titledRow == 0:
        return ("simple", totalHeaderRows, totalColumns)
    elif totalHeaderRows > 0 and titledRow > 0:
        return ("multidimensional", totalHeaderRows, totalColumns)
    else:
        logger.warning(f'Table type is unknown !')
        raise TypeError("Table type is unknown !")

def getTableHeader(_allRows):
    tableType, headerRowLength, totalTableColumns = getTableType(_allRows)
    tableRepr = []
    headerFirstRow = removeNewLines(_allRows[0].contents)
    # === 1. Get data of first row and start table list reprentation === #
    for cell in headerFirstRow:
        columnReprList = []
        # Get rowspans and colspans (convert to int or return None)
        rowspan, colspan = getSpans(cell)
        # Check for rowspan attribute in cell
        # Case 1 - Normal cell with no rowspan or colspan
        if rowspan == None and colspan == None:
            columnReprList = [cell.text.replace('\n', '')] # TO REMOVE ('replace') ===> HERE TO FORMAT !!!
            tableRepr.append(columnReprList)
        # Case 2 - Cell with rowspan BUT no colspan
        elif rowspan != None and colspan == None:
            # Insert element n times in column list representation according to rowspan
            for i in range(rowspan):
                columnReprList.append(cell.text)
            # Push column list in table representation
            tableRepr.append(columnReprList)
        # Case 3 - Cell with colspan BUT no rowspan
        elif colspan != None and rowspan == None:
            # Create new column list with element n times (depending on colspans)
            for i in range(colspan):
                columnReprList = []
                columnReprList.append(cell.text)
                tableRepr.append(columnReprList)
        # Case 4 - Cell with colspan AND rowspan
        elif colspan != None and rowspan != None:
            # Create new column list with element n times (depending on colspans)
            for i in range(colspan):
                columnReprList = []
                # Insert element in column list n times (depending on rowspan)
                for j in range(rowspan):
                    columnReprList.append(cell.text)
                # Insert column list
                tableRepr.append(columnReprList)

    # Log result so far
    logger.debug(f"[getTableHeader] TABLE FIRST ROW :\n{tableRepr} (length: {len(tableRepr)})")

    # Header have multiple cells ?
    if headerRowLength > 1:
        # === 2. Now that first row is done, insert other row of header (Skip first row since already done) === #
        for rowIndex, row in enumerate(_allRows[1:]):
            # Since we skipped first element, row index is out whack so re-adjust rowIndex at correct index
            rowIndex += 1
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
                        print(f'VALUE TO BE INSERTED : {cell.text}')
                        print(f'TESTED TABLE : {colList} AT INDEX {rowIndex}')
                        try:
                            # Check if index exists
                            colList[rowIndex]
                        except IndexError:
                            print(f"FREE ! INSERT VALUE '{cell.text}' and LEAVE LOOP")
                            # If not then spot is available for element
                            colList.insert(rowIndex, cell.text)
                            # Spot has been found, break loop
                            break
                        else:
                            print("OCCUPIED")
                            # Continue searching a spot in lists
                            continue
                # Case 2 - Cell with rowspans
                elif cell.get('rowspan') != None:
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
                # Case 3 - Cell with colspan
                elif cell.get('colspan') != None:
                    pass

    logger.debug(f"[getTableHeader] TABLE FINAL RESULT :\n{tableRepr}")
    return tableRepr

# ====== UNCOMMENT TO TEST HERE ====== #
getTableHeader(allRows)