import json
import os
from BandAPI.BandWiki import BandWiki

if __name__ == "__main__":
    wikiObj = BandWiki("Melvins")
    # Convert dict to pretty string for viewing
    # ensure_ascii=False to avoid weird characters are due to JSON.dump
    prettyDict = json.dumps(wikiObj.getAllInfos(), indent=4, ensure_ascii=False)
    print(prettyDict)