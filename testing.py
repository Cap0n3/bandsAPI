import unittest
from bs4 import BeautifulSoup
import requests
from BandAPI.BandWiki import BandWiki

#===========================#
#=== Test Data reference ===#
#===========================#

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

if __name__ == "__main__":
  unittest.main()