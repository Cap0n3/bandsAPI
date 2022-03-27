import requests
from bs4 import BeautifulSoup

def scrapStats(urlsList):
    '''
    Function to scrap specific artist's monthly listeners and followers from Open Spofify. 
    
    @Parameters : 
        urlList (url) : Takes a simple list with Open Spotify Artist's URL's.
    @Return : 
        Returns a multilevel dictionnary for each artist => Exemple : {'Slipknot': {'Monthly Listeners': '8,244,721', 'Followers': '7,481,658'}, etc ...}
    '''
    #Main dictionnary (will contain all results)
    allArtistsStats={}

    for url in urlsList:

        #Get page content
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception("Page doesn't exist or is not reachable ! \nProblematic URL : " + url)
        
        #Parse content
        soup = BeautifulSoup(response.text, 'html.parser')

        #Print soup result content in a file (for further html examination)
        # text = soup.prettify().encode("utf-8")
        # fp = open('webContent.txt', 'wb')
        # fp.write(text)
        # fp.close()

        #Get instersting lines from spotify page HTML
        artistName = soup.select("h1.view-header")
        listenersAndFollowers = soup.findAll('div', attrs={"insights__column"})

        #Dict that'll contain results (Listeners and followers)
        artistStat = {}

        #Extract monthly listeners and followers
        for el in listenersAndFollowers:
            category=el.span.text
            numbers=el.h3.text

            #Add values in dict
            artistStat[category]=numbers

        #Populate dict with artist name as key and artist stats as dict values (multilevel dict)
        allArtistsStats[artistName[0].text] = artistStat
    
    #Return reslults in multilevel dict
    return allArtistsStats

urls=["https://open.spotify.com/artist/05fG473iIaoy82BF1aGhL8", "https://open.spotify.com/artist/6Ghvu1VvMGScGpOUJBAHNH"]
RAWDataDict = scrapStats(urls)

print(RAWDataDict)

