from inspect import formatannotation
import os
from bs4 import BeautifulSoup
import re

# For Windows (relative path) 
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'debug_Table_Melvins.html')


with open(filename, 'r') as htmlTestFile:
    soup = BeautifulSoup(htmlTestFile, "html.parser")

allRows = soup.find_all("tr")

tableRepr = []
column = []

for row in allRows:
    # Extract row chilren
    rowChildren = row.contents
    # Remove \n char in child
    cleanRowChildren = list(filter(lambda x: False if x == "\n" else True, rowChildren))
    # Check for rowspans
    attributes = cleanRowChildren[0].attrs
    if attributes.get('rowspan') != None:
        print(cleanRowChildren[0])
    else:
        column.append(cleanRowChildren[0].text.replace('\n', ''))
    #firstChild = cleanRowChildren[0].text.replace('\n', '')
    #column.append(firstChild)

#print(column)