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
filename = os.path.join(dirname, 'tableHeader_case3.html')

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

# [STEP 2] - Get type of table (simple or multidimensional ?) and number of header rows
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
        Tuple with either "simple" or "multidimensional" string and number of header cells.
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
    # Final condition to decide type of tabe
    if totalHeaderRows > 0 and titledRow > 0:
        return ("multidimensional", totalHeaderRows)
    elif totalHeaderRows > 0 and titledRow == 0:
        return ("simple", totalHeaderRows)

tableType, rowStart = getTableType(allRows)

# [STEP 3] - Prepare table representation start with header data (for two type of table)
if tableType == "simple":
    pass


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

