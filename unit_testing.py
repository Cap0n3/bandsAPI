import unittest

from BandAPI.BandScrap import BandData

class test_main(unittest.TestCase):

    # === Object === #
    def setUp(self):
        self.bandDataObj = BandData("Nirvana")
    
    def tearDown(self):
        # Object destruction
        self.bandDataObj = None
    
    # === Testing === #
    def test_getAllInfos(self):
        resultDict = self.bandDataObj.getAllInfos()
        print(resultDict)

if __name__ == "__main__":
  unittest.main()