import os
from bs4 import BeautifulSoup

# For Windows (relative path) 
dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'debug_Table_Melvins.html')


with open(filename, 'r') as htmlTestFile:
    soup = BeautifulSoup(htmlTestFile, "html.parser")

print(soup.prettify())