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
from collections import namedtuple, OrderedDict
import json
import re


# For Windows (relative path) 
dirname = os.path.dirname(__file__)

# =========================================================== #
# ================== UNCOMMENT TO TEST HERE ================== #
# =========================================================== #
# filename = os.path.join(dirname, 'Test_Table_Header/11_tableHeader_case11.html')
filename = os.path.join(dirname, 'Test_Tables/debugTable_case0.html')
# Open html file
with open(filename, 'r') as htmlTestFile:
    soup = BeautifulSoup(htmlTestFile, "html.parser")
# Get table tag in soup
table = soup.find('table')

# Note : DON'T FORGET TO COMMENT/UNCOMMENT FUNCTION CALL AT THE END

# ========================== #
# ====== Logging init ====== #
# ========================== #

# logging.basicConfig(level=logging.NOTSET)
# logger = logging.getLogger(__name__)

# Init custom logger
logger = logging.getLogger(__name__)

# Init & add handler
stream_handler = logging.StreamHandler(sys.stdout) # To console
file_handler = logging.FileHandler(f"{dirname}/ExtractTableLog.log", mode='w') # To file
logger.addHandler(file_handler)

# Set format of log
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(log_format)

# Set min log levels I wanna see
logger.setLevel(logging.DEBUG)

class ExtractTable:
    def __init__(self, table):
        self.table = table
        # Extract rows (<tr>) from table soup
        self.allRows = self.table.find_all("tr")
    
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
    def insertRows(cell_data, rowSpan, colSpan, row_index, table_repr, whichRow):
        '''
        This utility method is the core of both `getTableHeader()` and `getTableHeader()` methods, it's here to keep code as DRY as possible.
        It insert cell data (content cleaned of any new line char) in given table list reprentation and take into account if there's rowspan 
        or colspan in cell attribute. It'll insert n times in same column list if there's a rowspan or insert data in consecutive column list 
        if there's a colspan. When finished it simply returns table list reprentation.

        Params
        ------
        `cell` : `<class 'bs4.element.Tag'>`
            BS4 cell from table (like `<th rowspan="2">Year</th>`).
        
        `rowSpan` : `int`
            Rowspan attribute of cell (number of rowpsan).
        
        `colSpan` : `int`
            Colspan attribute of cell (number of colpsan).

        `row_index` : `int`
            Row index of current `cell`.

        `table_repr` : `list`
            Nested list representing table (ex : [['Year'], ['Album'], ['Label']]).

        `whichRow` : `str`
            - Select `firstHeaderRow` if this is the very first row of table header.
            - Select `headerRow` if this is the second (or following) row of table header.
            - Select `firstBodyRow` if this is the very first row of table body.
            - Select `bodyRow` if this is the second (or following) row of table body.
        
        Returns
        -------
        tuple
            Tuple with rowspan and colspan (return None if there's no rowspan/colspan)
        '''
        logger.debug(f"-------------------------------------")
        logger.debug(f"[START] Entered insertRows() method !")
        logger.debug(f"[PARAMS] cell : {cell_data}, rowspan/colspan : {rowSpan}/{colSpan}, row index {row_index}, table : {table_repr}, which row : {whichRow}")
        # Clean cell and convert to text
        cleanedCell = cell_data.text.replace('\n', '')
        # === CONDITION TREE === #
        if whichRow == "firstHeaderRow":
            logger.debug(f"[*] TEST CELL {cell_data}")
            # === CASE 1 - Normal cell with NO rowspans and NO colspan === #
            if rowSpan == None and colSpan == None:
                logger.debug(f"[*] CASE 1 - NO ROWSPAN, NO COLSPAN")
                columnReprList = []
                columnReprList.append(cleanedCell)
                table_repr.append(columnReprList)
                logger.debug(f"[OK] Value '{cleanedCell}' inserted in table list representation !")
            # === CASE 2 - Cell WITH rowspan BUT NO colspan === #
            elif rowSpan != None and colSpan == None:
                logger.debug(f"[*] CASE 2 - ROWSPAN, NO COLSPAN")
                columnReprList = []
                # Insert element n times in column list representation according to rowspan
                for i in range(rowSpan):
                    columnReprList.append(cleanedCell)
                table_repr.append(columnReprList)
                logger.debug(f"[OK] Value '{cleanedCell}' inserted {rowSpan} times in table list representation !")
            # === CASE 3 - Cell WITH colspan BUT NO rowspan === #
            elif colSpan != None and rowSpan == None:
                logger.debug(f"[*] CASE 3 - COLSPAN, NO ROWSPAN")
                # Create new column list with element n times (depending on colspans)
                for i in range(colSpan):
                    columnReprList = []
                    columnReprList.append(cleanedCell)
                    table_repr.append(columnReprList)
                    logger.debug(f"[OK] Value '{cleanedCell}' inserted in {colSpan} columns in table list representation !")
            # === CASE 4 - Cell WITH colspan AND rowspan === #
            elif colSpan != None and rowSpan != None:
                logger.debug(f"\t[*] CASE 4 - COLSPAN, ROWSPAN")
                # Create new column list with element n times (depending on colspans)
                for i in range(colSpan):
                    columnReprList = []
                    # Insert element in column list n times (depending on rowspan)
                    for j in range(rowSpan):
                        columnReprList.append(cleanedCell)
                    logger.debug(f"[OK] Value '{cleanedCell}' inserted {rowSpan} times in table list representation !")
                    # Insert column list
                    table_repr.append(columnReprList)
                    logger.debug(f"[OK] Value '{cleanedCell}' inserted in {colSpan} columns in table list representation !")
            # Return modified list
            return table_repr
        elif whichRow == "headerRow":
            for colIndex, columnList in enumerate(table_repr):
                # For every case scenario, why try in index exists first
                try:
                    # -> Check if index exists in column
                    logger.debug(f"[*] TRY CELL '{cell_data}' FOR COLUMN INDEX {colIndex} AT ROW INDEX {row_index}")
                    columnList[row_index]
                # If an error occurs we then narrow to exact case scenario
                except IndexError:
                    # -> If index error then a spot is available for this element
                    logger.debug(f"[*] COLUMN : {columnList} AT INDEX {row_index}")
                    logger.debug(f"[*] VALUE TO BE INSERTED : {cleanedCell}")
                    # === CASE 1 - Normal cell with NO rowspans and NO colspan === #
                    if rowSpan == None and colSpan == None:
                        logger.debug(f"[*] CASE 1 - NO ROWSPAN, NO COLSPAN")
                        columnList.insert(row_index, cleanedCell)
                        logger.debug(f"\tValue '{cleanedCell}' inserted in column {columnList} !")
                    # === CASE 2 - Cell WITH rowspan BUT NO colspan === #
                    elif rowSpan != None and colSpan == None:
                        logger.debug(f"\t[*] CASE 2 - ROWSPAN, NO COLSPAN")
                        for spans in range(rowSpan):
                            columnList.insert(row_index + rowSpan, cleanedCell)
                        logger.debug(f"\tValue '{cleanedCell}' inserted {rowSpan} times in column {columnList} !")
                    # === CASE 3 - Cell WITH colspan BUT NO rowspan === #
                    elif colSpan != None and rowSpan == None:
                        logger.debug(f"\t[*] CASE 3 - COLSPAN, NO ROWSPAN")
                        columnList.insert(row_index, cleanedCell)
                        logger.debug(f"\tValue '{cleanedCell}' inserted in column {columnList} !")
                        table_repr[colIndex + (colSpan - 1)].insert(row_index, cleanedCell)
                        logger.debug(f"\tValue '{cleanedCell}' inserted in column at index {table_repr[colIndex + (colSpan - 1)]} !")
                    # === CASE 4 - Cell WITH colspan AND rowspan === #
                    elif colSpan != None and rowSpan != None:
                        logger.debug(f"\t[*] CASE 4 - COLSPAN, ROWSPAN")
                        for spans in range(rowSpan):
                            columnList.insert(row_index + rowSpan, cleanedCell)
                            table_repr[colIndex + (colSpan - 1)].insert(row_index + rowSpan, cleanedCell)
                    # -> Spot has been found so break loop
                    break
                else:
                    logger.debug(f"[*] COLUMN {colIndex} AT ROW {row_index} OCCUPIED, GO TO NEXT")
                    # Continue searching a spot in column lists
                    continue
            # Return modified list
            return table_repr
        elif whichRow == "firstBodyRow" :
            columnList = []
            # === CASE 1 - Normal cell with NO rowspans === #
            if rowSpan == None:
                logger.debug(f"[*] CASE 1 - NO ROWSPAN")
                columnList.append(cleanedCell)
                table_repr.append(columnList)
                logger.debug(f"[OK] Value '{cleanedCell}' inserted in table list representation !")
            # === CASE 2 - Cell WITH rowspan === #
            elif rowSpan != None:
                logger.debug(f"[*] CASE 2 - ROWSPAN")
                for i in range(rowSpan):
                    columnList.append(cleanedCell)
                table_repr.append(columnList)
                logger.debug(f"[OK] Value '{cleanedCell}' inserted {rowSpan} times in table list representation !")
            # Return modified list
            return table_repr
        elif whichRow == "bodyRow" :
            for colIndex, columnList in enumerate(table_repr):
                try:
                    # -> Check if index exists in column
                    logger.debug(f"[*] TRY CELL '{cell_data}' FOR COLUMN INDEX {colIndex} AT ROW INDEX {row_index}")
                    columnList[row_index]
                # If an error occurs we then narrow to exact case scenario
                except IndexError:
                    # === CASE 1 - Normal cell with NO rowspans === #
                    if rowSpan == None:
                        logger.debug(f"[*] CASE 1 - NO ROWSPAN")
                        table_repr[colIndex].append(cleanedCell)
                        logger.debug(f"[OK] Value '{cleanedCell}' inserted in table list representation !")
                    # === CASE 2 - Cell WITH rowspan === #
                    elif rowSpan != None:
                        logger.debug(f"[*] CASE 2 - ROWSPAN")
                        for i in range(rowSpan):
                            table_repr[colIndex].append(cleanedCell)
                        logger.debug(f"[OK] Value '{cleanedCell}' inserted {rowSpan} times in table list representation !")
                    break
                else:
                    logger.debug(f"[*] COLUMN {colIndex} AT ROW {row_index} OCCUPIED, GO TO NEXT")
                    # Index already exists, ok continue searching for a spot in columns (lists)
                    continue
            # Return modified list
            return table_repr        
        else:
            logger.warning(f"'{whichRow}' is not a valid argument for 'whichRow' parameter ! It should be either 'firstHeaderRow', 'headerRow' or 'normalRow'.")
            raise ValueError(f"'{whichRow}' is not a valid argument for 'whichRow' parameter ! \nIt should be either 'firstHeaderRow', 'headerRow', 'firstBodyRow' or 'bodyRow'.")

    # ============================== #
    # ========= MAIN FUNCS ========= #
    # ============================== #

    def getTableType(self):
        '''
        This method role is to determine table type and give some useful infos about table. 
        Type can be either simple (1D - One dimension) or multidimensional (2D - Two dimensions).
        
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
        `<class 'dict'>`
            - `dimentions` : Either "1D" or "2D" string 
            - `total_header_rows` : Header length (number of header rows)
            - `total_columns` : Total columns in table
            - `total_th_cells` : Total `<th>` cells in table
            - `total_th_cells` : Total `<td>` cells in table
        '''
        resultDict = {}
        totalHeaderRows = 0 # Row with only <th>
        totalTitledRow = 0 # Row with one <th> and then <td>
        totalThCells = 0
        totalTdCells = 0
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
                    totalThCells += 1
                elif content.name == "td":
                    tdCells += 1
                    totalTdCells += 1
            if contentCount == thCells:
                # There's only <th> in row (it's a header)
                totalHeaderRows += 1
                # logger.debug(f"Row {str(rowIndex)} - <th> count = {thCells}, <td> count = {tdCells} at  => it's a header row !")
            elif thCells == 1 and tdCells == (contentCount - 1):
                # There's one <th> and the rest are <td>, it's a multidimensional table
                totalTitledRow += 1
                # logger.debug(f"Row {str(rowIndex)} - <th> count = {thCells}, <td> count = {tdCells} at  => it's a titled row !")
        # === Poplulate result dictionnary === #
        # Final condition to decide type of table
        if totalHeaderRows > 0 and totalTitledRow == 0:
            # It's a one dimensionnal table
            resultDict['dimensions'] = "1D"
        elif totalHeaderRows > 0 and totalTitledRow > 0:
            # It's a two dimensionnal table
            resultDict['dimensions'] = "2D"
        elif totalThCells == 0 and totalTdCells > 0:
            # Case where only table body is given (uncommon ... mainly for testing)
            resultDict['dimensions'] = "1D"
        else:
            logger.warning(f'Table type is unknown ! Table rows :\n{self.allRows}')
            raise TypeError("Table type is unknown !")
        # Populate remaining infos
        resultDict['total_header_rows'] = totalHeaderRows
        resultDict['total_columns'] = totalColumns
        resultDict['total_th_cells'] = totalThCells
        resultDict['total_td_cells'] = totalTdCells

        return resultDict
    
    def getTableHeader(self):
        '''
        This method returns header table in a list reprentation. The "table list reprentation" is a nested list that look like 
        this `[['Year'], ['Album'], ['Label']]` (were "Year", "Album", "Label" are columns in first row). The second row would be
        inserted in the list like that `[['Year', 'Period'], ['Album', 'Release], ['Label', 'Company']]`.

        Note : Duplicated information represents either rowspans or colspans in header table.

        Parameters
        ----------
        `self.allRows` : `<class 'bs4.element.ResultSet'>`
            BS4 result set, look like this : [<tr><th>Year</th><th>Album</th><th>Label</th></tr>, etc...]
        
        Returns
        -------
        `list`
            Nested list representing table columns.
        '''
        # Get table type dict
        tableType = self.getTableType()
        logger.info(f"[TABLE INFO] Type : {tableType['dimensions']}, Header length : {tableType['total_header_rows']}, Total columns : {tableType['total_columns']}")
        headerRowLength = tableType['total_header_rows']
        # Init table reprentation
        tableRepr = []
        headerFirstRow = ExtractTable.removeNewLines(self.allRows[0].contents)
        # === 1. Get data of first row and start table list reprentation === #
        for cell in headerFirstRow:
            columnReprList = []
            # Get rowspans and colspans (if any the convert to int or return None)
            rowspan, colspan = ExtractTable.getSpans(cell)
            # Insert data in table reprentation
            tableRepr = ExtractTable.insertRows(cell, rowspan, colspan, 0, tableRepr, "firstHeaderRow")

        # Log result so far
        logger.info(f"[getTableHeader] TABLE FIRST ROW :\n{tableRepr} (length: {len(tableRepr)})")

        # Header have multiple cells ?
        if headerRowLength > 1:
            # === 2. Now that first row is done, insert other row of header (Skip first row since already done) === #
            for rowIndex, row in enumerate(self.allRows[1:]):
                # Since we skipped first element, row index is out whack so re-adjust rowIndex at correct index
                rowIndex += 1
                # Stop at end of table header
                if rowIndex == headerRowLength: break
                # Get row content and clean them
                rowChildren = ExtractTable.removeNewLines(row.contents)
                # Loop through elements and insert them in table list representation
                for cell in rowChildren:
                    # Get rowspans and colspans (if any the convert to int or return None)
                    rowspan, colspan = ExtractTable.getSpans(cell)
                    tableRepr = ExtractTable.insertRows(cell, rowspan, colspan, rowIndex, tableRepr, "headerRow")
        logger.debug(f"[getTableHeader] TABLE FINAL RESULT :\n{tableRepr}")
        return tableRepr

    def getTableBody(self):
        '''
        This method returns table body (not header) in a list reprentation. The "table list reprentation" is a nested list that look like 
        this `[['1991'], ['Bullhead'], ['Lysol Records']]` (were "1991", "Bullhead", "Lysol" are columns in first body row). The second row would be
        inserted in the list like that `[['1991', '1992'], ['Bullhead', 'Eggnog'], ['Lysol Records', 'Atlantic Records']]`.

        Note : Duplicated information represents rowspans table body. Colspans are not handled with this method.

        Parameters
        ----------
        `self.allRows` : `<class 'bs4.element.ResultSet'>`
            BS4 result set, look like this : [<tr><th>Year</th><th>Album</th><th>Label</th></tr>, etc...]
        
        Returns
        -------
        `list`
            Nested list representing table columns.
        '''
        tableBodyRepr = []
        # Get table type dict
        tableType = self.getTableType()
        headerRowLength = tableType['total_header_rows']
        for rowIndex, row in enumerate(self.allRows[headerRowLength:]):
            # Since we skipped header, row index is out whack so re-adjust rowIndex at correct index
            #rowIndex += headerRowLength
            # Get row content and clean them
            rowChildren = ExtractTable.removeNewLines(row.contents)
            #Loop through elements and insert them in table list representation
            for cell in rowChildren:
                # Get rowspans (if any the convert to int or return None)
                rowspan, colspan = ExtractTable.getSpans(cell)
                # If this is the first row
                if rowIndex == 0:
                    tableBodyRepr = ExtractTable.insertRows(cell, rowspan, colspan, rowIndex, tableBodyRepr, "firstBodyRow")
                    logger.info(f"Cell entered in the first row of table body !")
                    logger.info(f"{tableBodyRepr}")
                else:
                    tableBodyRepr = ExtractTable.insertRows(cell, rowspan, colspan, rowIndex, tableBodyRepr, "bodyRow")
                    logger.info(f"Cell entered in row of table body !")
                    logger.info(f"{tableBodyRepr}")
        return tableBodyRepr

    def getTableList(self):
        '''
        This method returns a table (header and body) in a list reprentation. The "table list reprentation" is a nested list that look like 
        this `[['Year', '1991','1992'], ['Album', 'Bullhead', 'Eggnog'], ['Label', 'Boner Records', 'Atlantic Records']]`. Here first element
        of nested lists represents column title, it can be duplicated if there was either a rowspan or a colspan attribute.

        Note : Duplicated information represents rowspans/colspans.
        
        Returns
        -------
        `list`
            Nested list representing table columns.
        '''
        # Get table header list
        tableHeader = self.getTableHeader()
        # Get table body list
        tableBody = self.getTableBody()
        # Check that tables are same length (right number of columns)
        assert len(tableHeader) == len(tableBody), "Table header & body don't have the same number of columns !"
        # Join all column lists to create full table reprentation
        tableRepr = []
        for colHeaderLst, colBodyLst in zip(tableHeader, tableBody):
            colHeaderLst.extend(colBodyLst)
            tableRepr.append(colHeaderLst)
        return tableRepr

    def getTableDict(self):
        resultDict = OrderedDict()
        # Get table header in list format
        tableHeaderList = self.getTableHeader()
        logger.debug(f"TABLE HEADER : \n{tableHeaderList}")
        # Get table body in list format
        tableBodyList = self.getTableBody()
        logger.debug(f"TABLE BODY : \n{tableBodyList}")
        # Check that tables are same length (right number of columns)
        assert len(tableHeaderList) == len(tableBodyList), "Table header & body don't have the same number of columns !"
        # Get table general infos
        tableType = self.getTableType()
        logger.info(f"[INFO] Table type : {tableType}")
        # It's a one dimensional table
        if tableType['dimensions'] == "1D":
            # === 1. Prepare dict keys with column header === #
            # IMPORTANT : it's an ordered dict, it preserve insertion order to later easily identify columns.
            # a. It's a simple table header with one header row
            if tableType['total_header_rows'] == 1:
                logger.debug("[*] Table header has only row.")
                for col in tableHeaderList:
                    # Prepare dict (insert keys)
                    resultDict[col[0]] = ""
            # b. It's a more complex table header with one multiple header rows
            elif tableType['total_header_rows'] > 1:
                logger.debug(f"[*] Table header has {tableType['total_header_rows']} rows.")
                pass
            # === 2. Insert data from table body in dict === #
            # Since insertion order in dict was preserved we can easily for right column 
            for key, col in zip(resultDict, tableBodyList):
                colElementList = [el for el in col]
                resultDict[key] = colElementList
            
            return dict(resultDict)
        # It's a two dimensional table           
        elif tableType['dimensions'] == "2D":
            pass
            
# ====== UNCOMMENT TO TEST HERE ====== #
tableObj = ExtractTable(table)
# tableHeaderList = tableObj.getTableHeader()
# tableBodyList = tableObj.getTableBody()
# fullTable = tableObj.getTableList()
print(tableObj.getTableDict())