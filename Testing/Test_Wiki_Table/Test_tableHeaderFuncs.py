'''
This file is a test file to develop the ExtractTable class which will be used in 
main BandWiki class. 

> Important ! The code below main should be exactly like in BandWiki.py.
'''

from inspect import formatannotation
import os
import logging
import sys
from bs4 import BeautifulSoup
from collections import namedtuple
import json
import re

# ============ UNCOMMENT TO TEST HERE ============ #
# For Windows (relative path) 
dirname = os.path.dirname(__file__)
# filename = os.path.join(dirname, 'Test_Table_Header/11_tableHeader_case11.html')
filename = os.path.join(dirname, 'Test_Tables/debugTable_case4.html')
# Open html file
with open(filename, 'r') as htmlTestFile:
    soup = BeautifulSoup(htmlTestFile, "html.parser")
allRows = soup.find_all("tr")
# ============================================== #
# DON'T FORGET TO COMMENT/UNCOMMENT FUNCTION CALL AT THE END
# ============================================== #
# ============================================== #


# ========================== #
# ====== Logging init ====== #
# ========================== #

# logging.basicConfig(level=logging.NOTSET)
# logger = logging.getLogger(__name__)

# Init custom logger
logger = logging.getLogger(__name__)

# Init & add handler
stream_handler = logging.StreamHandler(sys.stdout) # To console
# file_handler = logging.FileHandler('file.log') # To file
logger.addHandler(stream_handler)

# Set format of log
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(log_format)

# Set min log levels I wanna see
logger.setLevel(logging.WARNING)

class ExtractTable:
    def __init__(self, allRows):
        self.allRows = allRows
    
    # ===================================== #
    # ========= UTILITY FUNCTIONS ========= #
    # ===================================== #
    @staticmethod 
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

    @staticmethod 
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

    @staticmethod 
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

    @staticmethod 
    def insertRows(cell_data, rowSpan, colSpan, row_index, table_repr, firstRow=False):
        if firstRow:
            # === CASE 1 - Normal cell with NO rowspans and NO colspan === #
            if rowSpan == None and colSpan == None:
                columnReprList = []
                columnReprList.append(cell_data.text)
                table_repr.append(columnReprList)
            # === CASE 2 - Cell WITH rowspan BUT NO colspan === #
            elif rowSpan != None and colSpan == None:
                columnReprList = []
                # Insert element n times in column list representation according to rowspan
                for i in range(rowSpan):
                    columnReprList.append(cell_data.text)
                table_repr.append(columnReprList)
            # === CASE 3 - Cell WITH colspan BUT NO rowspan === #
            elif colSpan != None and rowSpan == None:
                # Create new column list with element n times (depending on colspans)
                for i in range(colSpan):
                    columnReprList = []
                    columnReprList.append(cell_data.text)
                    table_repr.append(columnReprList)
            # === CASE 4 - Cell WITH colspan AND rowspan === #
            elif colSpan != None and rowSpan != None:
                # Create new column list with element n times (depending on colspans)
                for i in range(colSpan):
                    columnReprList = []
                    # Insert element in column list n times (depending on rowspan)
                    for j in range(rowSpan):
                        columnReprList.append(cell_data.text)
                    # Insert column list
                    table_repr.append(columnReprList)
            # Return modified list
            return table_repr
        else:
            for colIndex, columnList in enumerate(table_repr):
                # For every case scenario, why try in index exists first
                try:
                    # -> Check if index exists in column
                    columnList[row_index]
                # If an error occurs we then narrow to exact case scenario
                except IndexError:
                    # -> If index error then a spot is available for this element
                    logger.debug(f'[*] COLUMN : {columnList} AT INDEX {row_index}')
                    logger.debug(f'[*] VALUE TO BE INSERTED : {cell_data.text}')
                    # === CASE 1 - Normal cell with NO rowspans and NO colspan === #
                    if rowSpan == None and colSpan == None:
                        logger.debug(f"\t[* CASE 1 *] - NO ROWSPAN, NO COLSPAN")
                        columnList.insert(row_index, cell_data.text)
                        logger.debug(f"\tValue '{cell_data.text}' inserted in column {columnList} !")
                    # === CASE 2 - Cell WITH rowspan BUT NO colspan === #
                    elif rowSpan != None and colSpan == None:
                        logger.debug(f"\t[* CASE 2 *] - ROWSPAN, NO COLSPAN")
                        for spans in range(rowSpan):
                            columnList.insert(row_index + rowSpan, cell_data.text)
                        logger.debug(f"\tValue '{cell_data.text}' inserted {rowSpan} times in column {columnList} !")
                    # === CASE 3 - Cell WITH colspan BUT NO rowspan === #
                    elif colSpan != None and rowSpan == None:
                        logger.debug(f"\t[* CASE 3 *] - COLSPAN, NO ROWSPAN")
                        columnList.insert(row_index, cell_data.text)
                        logger.debug(f"\tValue '{cell_data.text}' inserted in column {columnList} !")
                        table_repr[colIndex + (colSpan - 1)].insert(row_index, cell_data.text)
                        logger.debug(f"\tValue '{cell_data.text}' inserted in column at index {table_repr[colIndex + (colSpan - 1)]} !")
                    # === CASE 4 - Cell WITH colspan AND rowspan === #
                    elif colSpan != None and rowSpan != None:
                        logger.debug(f"\t[* CASE 4 *] - COLSPAN, ROWSPAN")
                        for spans in range(rowSpan):
                            columnList.insert(row_index + rowSpan, cell_data.text)
                            table_repr[colIndex + (colSpan - 1)].insert(row_index + rowSpan, cell_data.text)
                    # -> Spot has been found so break loop
                    break
                else:
                    logger.debug(f"[*] COLUMN {colIndex} AT ROW {row_index} OCCUPIED, GO TO NEXT")
                    # Continue searching a spot in column lists
                    continue
            # Return modified list
            return table_repr

    # ============================== #
    # ========= MAIN FUNCS ========= #
    # ============================== #

    def getTableType(self):
        '''
        This method role is to determine table type and give some useful infos about table. 
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
        `self.allRows` : `<class 'bs4.element.ResultSet'>`
            BS4 result set, look like this : [<tr><td>Year</td><td>Album</td><td>Label</td></tr>, etc...]
        
        Returns
        -------
        `tuple[str, int, int]`
            Tuple with either "simple" or "multidimensional" string, header length (number of header rows) and total columns in table.
        '''
        totalHeaderRows = 0 # Row with only <th>
        titledRow = 0 # Row with one <th> and then <td>

        # Go through 10 first rows to get type of table
        for rowIndex, row in enumerate(self.allRows):
            thCells = 0
            tdCells = 0
            if rowIndex == 9:
                break
            # Get row contents
            rowContents = row.contents
            contentCount = len(ExtractTable.removeNewLines(rowContents))
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

    def getTableHeader(self):
        '''
        This method returns only header table in a list reprentation. The table list reprentation is a nested list that lool like 
        this `[['Year'], ['Album'], ['Label']]` (were "Year", "Album", "Label" are columns in first row). The second row would be
        inserted in list like that `[['Year', 'Period'], ['Album', 'Release], ['Label', 'Company']]`.

        Note : Duplicated information represents either rowspans or colspans in header table.

        Parameters
        ----------
        `self.allRows` : `<class 'bs4.element.ResultSet'>`
            BS4 result set, look like this : [<tr><th>Year</th><th>Album</th><th>Label</th></tr>, etc...]
        
        Returns
        -------
        `list`
            Nested list of table columns.
        '''
        # Get header row length
        funcTupleRes = self.getTableType()
        headerRowLength = funcTupleRes[1]
        # Init table reprentation
        tableRepr = []
        headerFirstRow = ExtractTable.removeNewLines(self.allRows[0].contents)
        # === 1. Get data of first row and start table list reprentation === #
        for cell in headerFirstRow:
            columnReprList = []
            # Get rowspans and colspans (if any the convert to int or return None)
            rowspan, colspan = ExtractTable.getSpans(cell)
            # Insert data in table reprentation
            tableRepr = ExtractTable.insertRows(cell, rowspan, colspan, 0, tableRepr, firstRow=True)

        # Log result so far
        logger.info(f"[getTableHeader] TABLE FIRST ROW :\n{tableRepr} (length: {len(tableRepr)})")

        # Header have multiple cells ?
        if headerRowLength > 1:
            # === 2. Now that first row is done, insert other row of header (Skip first row since already done) === #
            for rowIndex, row in enumerate(self.allRows[1:]):
                # Since we skipped first element, row index is out whack so re-adjust rowIndex at correct index
                rowIndex += 1
                # Stop at end of table header
                #if rowIndex == headerRowLength: break
                # Get row content and clean them
                rowChildren = ExtractTable.removeNewLines(row.contents)
                # Loop through elements and insert them in table list representation
                for cell in rowChildren:
                    # Get rowspans and colspans (if any the convert to int or return None)
                    rowspan, colspan = ExtractTable.getSpans(cell)
                    tableRepr = ExtractTable.insertRows(cell, rowspan, colspan, rowIndex, tableRepr)
                    

        logger.debug(f"[getTableHeader] TABLE FINAL RESULT :\n{tableRepr}")
        return tableRepr

    def getTableBody(self):
        tableBodyRepr = []
        # Get header row length
        funcTupleRes = self.getTableType()
        headerRowLength = funcTupleRes[1]
        headerRowIndex = headerRowLength
        for rowIndex, row in enumerate(self.allRows[headerRowIndex:]):
            # Since we skipped header, row index is out whack so re-adjust rowIndex at correct index
            rowIndex += headerRowIndex
            # Get row content and clean them
            rowChildren = ExtractTable.removeNewLines(row.contents)
            #Loop through elements and insert them in table list representation
            for cell in rowChildren:
                print(cell)
                # Get rowspans and colspans (if any the convert to int or return None)
                rowspan, colspan = ExtractTable.getSpans(cell)
                tableBodyRepr = ExtractTable.insertRows(cell, rowspan, colspan, rowIndex, tableBodyRepr)
        return tableBodyRepr


# ====== UNCOMMENT TO TEST HERE ====== #
tableObj = ExtractTable(allRows)
# tableList = tableObj.getTableHeader()
tableList = tableObj.getTableBody()
print(tableList)