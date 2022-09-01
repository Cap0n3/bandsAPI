import unittest
import os
import sys
import re
import inspect
from bs4 import BeautifulSoup
import requests
import json

# Go to parent folder to find modules (it's so stupid to have to do that ...)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

# Import class & functions
from BandAPI.BandWiki import BandWiki
from Test_Wiki_Table import Test_tableHeaderFuncs

#================#
#=== Settings ===#
#================#

PATH = os.path.dirname(os.path.realpath(__file__))

#===========================#
#=== Test Data reference ===#
#===========================#

BAND_LIST = ["Nirvana", "Queens of the stone age", "Knocked Loose", "Korn", "Mastodon", "Melvins", "Pearl jam", "Graveyard"]

TEST_MAIN_DICT = {
    'Origin': 'Aberdeen, Washington, U.S.', 
    'Genres': ['Grunge', 'alternative rock', 'punk rock', 'hard rock'], 
    'Years active': '1987–1994', 
    'Labels': ['Sub Pop', 'DGC'], 
    'Associated acts': ['Foo Fighters', 'Fecal Matter', 'Melvins', 'Scream', 'Sweet 75', 'Giants in the Trees'], 
    'Website': 'nirvana.com', 
    'Past members': ['Kurt Cobain', 'Krist Novoselic', 'Dave Grohl'], 
    'Discography': ['Bleach (1989)', 'Nevermind (1991)', 'In Utero (1993)']
}

TEST_DISCO_LIST = ['Bleach (1989)', 'Nevermind (1991)', 'In Utero (1993)']

#===========================#
#========= Testing =========#
#===========================#

@unittest.skip("Comment here to test")
class test_BandWiki(unittest.TestCase):
    # Setting Up
    def setUp(self):
        self.bandDataObj = BandWiki("Nirvana")
    
    def tearDown(self):
        self.bandDataObj = None
    
    # === Testing === #
    def test_getUlDiscography(self):
        html = requests.get("https://en.wikipedia.org/wiki/Nirvana_(band)").content
        self.testSoup = BeautifulSoup(html, "html.parser")
        resultList = self.bandDataObj.getUlDiscography(self.testSoup)
        self.assertListEqual(resultList, TEST_DISCO_LIST)

    def test_getAllInfos(self):
        resultDict = self.bandDataObj.getAllInfos()
        self.assertDictEqual(resultDict, TEST_MAIN_DICT)

    #@unittest.skip("To check dictionnaries, comment this line")
    def test_OutputDict(self):
        '''
        This test method is not regular, I just need it to test outputs for several
        bands dictionnaries (a sort of parametrization) but without the need of assert.

        If needed, it'll print all output dictionnaries in a file named 'dictToReview.txt' 
        to review later in order to check if resulting wikipedia scrap is clean or not.
        '''
        fileExists = os.path.exists(f"{PATH}/dictToReview.txt")
        if fileExists :
            os.remove(f"{PATH}/dictToReview.txt")
        
        for band in BAND_LIST:
            with open(f"{PATH}/dictToReview.txt", "a") as file:
                wikiObj = BandWiki(band).getAllInfos()
                prettyDict = json.dumps(wikiObj, indent=4, ensure_ascii=False)
                file.write(f"### (DICT START) ###\n\n")
                file.write(f"# ================= {band} ================= #\n\n")
                file.write(prettyDict)
                file.write(f"\n\n### (DICT END) ###\n\n")

class test_Functions(unittest.TestCase):
    '''
    Test for prototypes methods of BandWiki class.
    '''
    def setUp(self):
        # Get current folder
        self.dirname = os.path.dirname(__file__)
        # Set folder path to test table headers
        self.tableHeaderFilesFolder = os.path.join(self.dirname, "Test_Wiki_Table/Test_Table_Header")
    
    def test_getTableHeader(self):
        # =========== INIT - HERE TO FINE TUNE TEST ============ #
        # ====================================================== # 
        # Leave it to 'None' to test all cases, give case to test a particular file (ex : "case1" or "case5")
        testParticularCase = None
        # ====================================================== # 
        # ====================================================== # 
        # Test cases (expected results), all files in Test_Table_Header folder should be here !
        testTableHeaders = {
            "case0" : [['Year'], ['Album'], ['Label'], ['Note']],
            "case1" : [['Year', 'Year'], ['Album', 'Album'], ['Label', 'Label'], ['Note', 'About']],
            "case2" : [['Year', 'Year'], ['Album', 'Release'], ['Label', 'Label'], ['Note', 'About']],
            "case3" : [['Album', 'Release'], ['Year', 'Year'], ['Label', 'Label'], ['Note', 'About']],
            "case4" : [['Year', 'Year', 'Period'], ['Album', 'Album', 'Release'], ['Label', 'Label', 'Label'], ['Note', 'About', 'Facts']],
            "case5" : [['Year', 'Year', 'Period'], ['Album', 'Release', 'Record'], ['Label', 'Label', 'Company'], ['Note', 'About', 'Facts']],
            "case6" : [['Album', 'Album'], ['Details', 'Details'], ['Charts', 'USA'], ['Charts', 'EU'], ['Certifications', 'Certifications']],
            "case7" : [['Album', 'Release'], ['Details', 'Details'], ['Charts', 'USA'], ['Charts', 'EU'], ['Certifications', 'Awards']],
            "case8" : [['Album', 'Release', 'CD'], ['Details', 'Details', 'Details'], ['Charts', 'USA', 'USA'], ['Charts', 'EU', 'Germany'], ['Certifications', 'Awards', 'Awards']],
            "case9" : [['Album', 'Release', 'CD'], ['Details', 'Details', 'Details'], ['Charts', 'Charts', 'USA'], ['Charts', 'Charts', 'EU'], ['Certifications', 'Awards', 'Awards']],
            "case10" : [['Album', 'Release'], ['Details', 'Details'], ['CD Sales', 'EU'], ['Vinyl Sales', 'EU'], ['Certifications', 'Awards']],
            "case11" : [['Album', 'Album', 'Album'], ['Details', 'Details', 'Infos'], ['CD Sales', 'EU', 'SKU1'], ['Vinyl Sales', 'EU', 'SKU2'], ['Certifications', 'Awards', 'Awards']],
            "case12" : [['Album', 'Album', 'Album'], ['Details', 'Details', 'Infos'], ['CD Sales', 'EU', 'EU'], ['Vinyl Sales', 'EU', 'EU'], ['Certifications', 'Awards', 'Rewards']],
        }
        # ====== Utils Functions ====== #
        def sortByCase(element):
            '''
            Function to sort files by case number in list of files.
            '''
            res = re.findall(r'case\d+', element)
            num = re.findall(r'\d+', res[0])
            return int(num[0])
        
        # === Test all cases (all files) === #
        if testParticularCase == None :
            # Get list of files in dir (and sort them)
            files = [f for f in sorted(os.listdir(self.tableHeaderFilesFolder))]
            # Add complete path for all file in list
            allFiles = map(lambda file: os.path.join(self.tableHeaderFilesFolder, file), files)
            # Filter out folders from list
            filteredObj = filter(lambda file: os.path.isfile(file), allFiles)
            allFiles = list(filteredObj)
            # Sort files by case in list (they aren't sorted properly by sorted() above)
            allFiles.sort(key=sortByCase)
            # Get keys (case number) in list
            allCasesList = list(testTableHeaders.keys())
            # Loop throught files and test each one
            for file, case in zip(allFiles, allCasesList):
                print(f'\n[*] TEST FILE {file} FOR {case}\n')
                # Open file
                with open(file, 'r') as htmlTestFile:
                    soup = BeautifulSoup(htmlTestFile, "html.parser")
                # Extract rows from soup
                allRows = soup.find_all("tr")
                # Test function
                result = Test_tableHeaderFuncs.getTableHeader(allRows)
                self.assertEqual(result,  testTableHeaders[case])
        # === Test one particular case === #
        elif testParticularCase != None:
            filename = os.path.join(self.dirname, f'{self.tableHeaderFilesFolder}/tableHeader_{testParticularCase}.html')
            with open(filename, 'r') as htmlTestFile:
                soup = BeautifulSoup(htmlTestFile, "html.parser")
            # Extract rows from soup
            allRows = soup.find_all("tr")
            # Test function
            result = Test_tableHeaderFuncs.getTableHeader(allRows)
            self.assertEqual(result, testTableHeaders[testParticularCase])

if __name__ == "__main__":
  unittest.main()