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

# [STEP 2] - Get first row & scan type of cells
headerRow = removeNewLines(allRows[0].contents)


for rowIndex, row in enumerate(allRows):
    thCells = 0
    tdCells = 0
    rowContents = row.contents
    contentCount = len(removeNewLines(rowContents))
    # Count type cells in row
    for content in rowContents:
        if content.name == "th":
            thCells += 1
        elif content.name == "td":
            tdCells += 1
    # There's only <th> in row (it's a header)
    if contentCount == thCells:
        print(f"All <th> at row {str(rowIndex)} : it's a header row !")


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

