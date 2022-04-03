import json
from BandAPI.BandWiki import BandWiki

if __name__ == "__main__":
    wikiObj = BandWiki("Queens of the stone age")
    # Convert dict to pretty string for viewing (weird characters are due to JSON.dump)
    prettyDict = json.dumps(wikiObj.getAllInfos(), indent=4, ensure_ascii=False)
    print(prettyDict)

    #print(BandWiki("Nirvana").getAllInfos())