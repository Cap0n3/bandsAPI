'''
File to do random testing about anything that's needed.
'''
import os
from bs4 import BeautifulSoup
from BandAPI.CustomPackage.ExtractTableMod import ExtractTable

# For Windows (relative path) 
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'Test_Tables/debugTable_case0.html')

# Open html file
with open(filename, 'r') as htmlTestFile:
    soup = BeautifulSoup(htmlTestFile, "html.parser")

# Get table tag in soup
tableSoup = soup.find('table')

# Relative path
relPath = "Test_Wiki_Table/Test_Tables/debugTable_case0.html"

# ========= TESTING ========= #
tableObj = ExtractTable(tableSoup)
