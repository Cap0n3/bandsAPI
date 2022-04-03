import unittest
import os
import sys
import inspect
from bs4 import BeautifulSoup
import requests
import json

# Go to parent folder to find modules (it's so stupid to have to do that ...)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

from BandAPI.BandWiki import BandWiki

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

if __name__ == "__main__":
  unittest.main()