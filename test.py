import re
import urllib

import urllib2
from bs4 import BeautifulSoup
import spacy

from langdetect import detect

nlp = spacy.load('en')

 
def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True


from google import search, get_page
term = "justin gawrilow"
all_ents = {}
for i,url in enumerate(search(term, stop=1)):
    print url
    try:
        html = get_page(url)
        soup = BeautifulSoup(html, "lxml")
        data = soup.findAll(text=True)
        result = filter(visible, data)
        text = " ".join(result)
        doc = nlp(text)
        #for i in doc:
        #    print i.is_stop
        for ent in doc.ents:
            #print ent.label_, ent.text
            t = ent.text.strip()
            all_ents[t] = all_ents.get(t,[])
            all_ents[t].append((ent.label))
    except urllib2.HTTPError:
        print "Failure"
#
for key, value in sorted(all_ents.iteritems(), key=lambda (k,v): (len(v),k), reverse=True):
    print key, len(value)
    #apples = nlp(u"apples")
    #oranges = nlp(u"oranges")
    #print apples.similarity(oranges)
    #print detect(text)
    #break


