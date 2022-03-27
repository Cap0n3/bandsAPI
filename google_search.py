from googlesearch import search

res = search("Code of conduct Swiss band music", lang="fr")

for url in res:
    print(url)