import json
import os
from BandAPI.BandWiki import BandWiki


PATH = os.path.dirname(os.path.realpath(__file__))

BAND_LIST = ["Nirvana", "Queens of the stone age", "Knocked Loose", "Korn"]

if __name__ == "__main__":
    wikiObj = BandWiki("Queens of the stone age")
    # Convert dict to pretty string for viewing
    # ensure_ascii=False to avoid weird characters are due to JSON.dump
    prettyDict = json.dumps(wikiObj.getAllInfos(), indent=4, ensure_ascii=False)
    print(prettyDict)