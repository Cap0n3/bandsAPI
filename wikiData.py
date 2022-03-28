import requests
import re

URL = "https://www.wikidata.org/w/api.php"



QUERY = "Metallica"


params = {
    "action" : "wbsearchentities",
    "language" : "en",
    "format" : "json",
    "search" : QUERY 
}

try:
    # Search in Wikidata
    data = requests.get(URL,params=params)
    results = data.json()["search"]

    # Filter results and get ID of band's page
    for result in results:
        searchDescription = result["description"]
        isItBand = re.search(r'\bband\b', searchDescription, re.I)
        if isItBand != None:
            pageID = result["id"]
            
            #foo = requests.get(f"https://www.wikidata.org/wiki/{pageID}")
            #print(foo.content)

            # Don't go after first occurence of word 'band'
            break

except:
    print("Invalid Input try again !!!")