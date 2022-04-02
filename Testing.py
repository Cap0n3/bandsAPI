import unittest
import random
from BandScrap import BandData

class test_main(unittest.TestCase):

    # === Object === #
    def setUp(self):
        BANDS = ["Nirvana", "Knocked Loose", "Queens of the stone age"]
        bandChoice1 = random.choice(BANDS)
        bandChoice2 = random.choice(BANDS)
        while bandChoice1 == bandChoice2:
            bandChoice1 = random.choice(BANDS)
            bandChoice2 = random.choice(BANDS)
        
        self.bandDataObj1 = BandData(bandChoice1)
        self.bandDataObj2 = BandData(bandChoice2)
    
    def tearDown(self):
        # Object destruction
        self.bandDataObj1 = None
        self.bandDataObj2 = None
    
    # === Testing === #
    def test_getAllInfos(self):
        resultDict1 = self.bandDataObj1.getAllInfos()
        resultDict2 = self.bandDataObj2.getAllInfos()
        print(resultDict1)
        print(resultDict2)

if __name__ == "__main__":
  unittest.main()