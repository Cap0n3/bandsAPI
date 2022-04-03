from BandAPI.BandWiki import BandWiki

if __name__ == "__main__":
    wikiObj = BandWiki("Queens of the stone age")
    print(wikiObj.getAllInfos())