from google import search
import codecs
import operator



term = "rafiq380@yahoo.co.in"

fmap = {}

dp = "/Volumes/JB5T/georgia_tech/dumps/majorgeeks.txt"

lines = 0
with codecs.open(dp,encoding="utf-8",errors="ignore") as inf:
    for line in inf:
        charmap = {}
        lines += 1
        for c in line.strip():
            charmap[c] = charmap.get(c,0) + 1
        print lines
        for c in charmap:
            fmap[c] = fmap.get(c,{})
            fmap[c][charmap[c]] = fmap[c].get(charmap[c],0) + 1


def gethighest(x):
    mm = 0
    for m in fmap[x]:
        if fmap[x][m] > mm:
            mm = fmap[x][m]
    return (x,mm)


highest = sorted(map(gethighest,fmap.keys()),key=lambda tup:tup[1],reverse=True)
print highest[:10]






'''

for url in search(term, stop=30):
    print url
'''