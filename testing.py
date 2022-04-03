import unittest

from BandAPI.BandWiki import BandWiki

class test_main(unittest.TestCase):

    # === Object === #
    def setUp(self):
        self.bandDataObj = BandWiki("Nirvana")
    
    def tearDown(self):
        # Object destruction
        self.bandDataObj = None
    
    # === Testing === #
    def test_getAllInfos(self):
        resultDict = self.bandDataObj.getAllInfos()
        print(resultDict)

if __name__ == "__main__":
  unittest.main()