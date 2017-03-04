from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from json import loads, dumps
from datetime import datetime
from socketIO_client import SocketIO, LoggingNamespace
from google import search
from datetime import datetime
import time
from bs4 import BeautifulSoup
import urllib2
import pattern
from pattern.web import Twitter, plaintext
import urllib
from sklearn.feature_extraction import FeatureHasher
from sklearn import preprocessing
from tsne import bh_sne
from nltk.tokenize import word_tokenize
import urlparse

import spacy
import re
from faker import Faker
fake = Faker()
import html2text

import lassie
import tldextract
from sklearn.decomposition import PCA

from elasticsearch import Elasticsearch
import codecs
import sys

import spacy

nlp = spacy.load('en')


# Try this for entire  DB
# Try this for various data types


# Hook this back into user designated data

# Embedding of web pages?? based on several features
# google entry point as 2d map

# embedding of names

'''
1) start with first search e.g., justin gawrilow + washington dc
2) results matching this we should start searches for those terms based on neighboring terms
3) remove other terms

'''

class MyHandler(BaseHTTPRequestHandler):

    def rank_terms(self,text):
        all_ents = {}
        doc = nlp(text)
        for ent in doc.ents:
            t = ent.text.strip()
            all_ents[t] = all_ents.get(t,[])
            all_ents[t].append((ent.label))
            final_d = sorted(all_ents.iteritems(), key=lambda (k,v): (len(v),k), reverse=True)

        return {"terms":[{"term":key,"count":len(value)} for key,value in final_d][:10]}

    def do_webpage(self,url):
        response = urllib2.urlopen(url)
        html = response.read()
        soup = BeautifulSoup(html, "lxml")
        data = soup.findAll(text=True)
        result = filter(self.visible, data)
        text = " ".join(result)
        return text

    def visible(self,element):
        if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
            return False
        elif re.match('<!--.*-->', str(element.encode('utf-8'))):
            return False
        return True


    def do_POST(self):
        length = int(self.headers['Content-Length'])
        data = loads(self.rfile.read(length))
        print dumps(data)
        date = datetime.utcfromtimestamp(data["time"] / 1000.)
        data["time"] = date.isoformat("T").split(".")[0]
        del data["favicon"]
        del data["key"]

        # self.server.socketIO.emit('google',dumps(data))

        if data["url"] == None or data["url"].startswith("http://localhost:3000/") or \
        data["url"] == "chrome://newtab/" or data["url"] == "chrome://extensions/" or \
        data["url"].startswith("https://mail.google.com/"):
            return 

        elif any(map(data["url"].startswith,map(lambda x: x["urls"][0],social_mappings))):
            print "SOCIAL!!!"
            self.server.socketIO.emit('social_media',dumps({"account":data["url"]}))
            return

        elif data["url"].startswith("https://www.google.com/search") or \
        data["url"].startswith("https://www.google.com/webhp"):
            print data["url"]

            parsed = urlparse.urlparse(data["url"])
            if 'q' in urlparse.parse_qs(parsed.query):
                q = urlparse.parse_qs(parsed.query)['q']
            else:
                try:
                    q = data["url"].split("#q=")[1].split("&")[0]
                except IndexError:
                    print "No search term found"
                    return
            print "Google search -> ", q
            self.server.socketIO.emit('google_search',dumps({"q":q}))
            #urls = self.server.google_scrape(q,self.server.social_mappings,self.server.urls_to_content)
            #embedding = self.server.embed(urls)
            #embed_json = map(lambda x: {"url":x[0],"x":x[1],"y":x[2]},embedding)
            #print dumps(embed_json)

            # LIGHTS search hold off for now
            #results = lights_search(q)
            #self.server.socketIO.emit("dark_search",results)
            #self.server.socketIO.emit('google',dumps(embed_json))
            return


        elif data["url"] not in self.server.url_dict:
            print "Unseen URL:", dumps(data)
            text = self.do_webpage(data["url"])
            self.server.url_dict[data["url"]] = {"url":data["url"], "text":None,"total_time":None,"count":1,"id":"p"+str(len(self.server.url_dict))}
            self.server.socketIO.emit('new_page',dumps(self.server.url_dict[data["url"]]))
            self.server.socketIO.emit('terms',dumps(self.rank_terms(text)))
            '''
                TODO:
                1) check what site it is...if google..do look ahead
                2) otherwise...download html..parse out stuff...
                3) supply option to check out entire domain?
                4) deep search, passive search
                5) run featurization, update embeding..display

            '''
        elif data["url"] in self.server.url_dict:
            print "Previously seen URL", dumps(data)
            self.server.url_dict[data["url"]]["count"] += 1
            self.server.socketIO.emit('old_page',dumps(self.server.url_dict[data["url"]]))
        #self.fh.write(dumps(data) + "\n")
        #self.fh.flush()
        #self.send_response(202)
        #self.end_headers()
        return


if __name__ == "__main__":

    social_mappings = [{"site":"LINKEDIN","urls":["https://www.linkedin.com/in/"]},
    {"site":"INSTAGRAM","urls":["https://www.instagram.com/"]},
    {"site":"GITHUB","urls":["https://github.com/"]},
    {"site":"PINTEREST","urls":["https://www.pinterest.com/"]},
    {"site":"INSTAGRAM","urls":["https://www.instagram.com/"]},
    {"site":"FACEBOOK","urls":["https://www.facebook.com/"]},
    {"site":"TWITTER","urls":["https://twitter.com/"]},
    {"site":"F6S","urls":["https://www.f6s.com/"]}
    ]


    def lights_search(text):
        text = text.strip()
        QUERY = 'text:"'+text+'"'
        DOC_TYPE = ""
        #res = es.search(index="onions", doc_type=DOC_TYPE, q=QUERY)
        print dumps(res,indent=2)
        size = res['hits']['total']
        print "Index onions/%s size is %d" % (DOC_TYPE, size)

        results = [{"domain":x["_source"]["domain"],"url":x["_source"]["url"],"title":x["_source"]["title"],"text":x["_source"]["text"][:50]} for x in res['hits']['hits'] if "url" in x["_source"]]
        return {"size":size,"results":results}


    def embed(data):
        print "running embed..."
        D = []
        Socials = []
        Sites = []
        dSet = set()
        for (url,text,site_type) in data:
            if site_type == "TEXT":
                print "embedding...", url
                letters = {}
                words = word_tokenize(text)
                for char in words:
                    letters[char] = letters.get(char,0) + 1
                    dSet.add(char)
                D.append(letters)
                Sites.append((url,text,site_type))
            else:
                Socials.append((url,text,site_type))
                #print letters

        h = FeatureHasher(n_features=len(dSet))
        f = h.transform(D)
        df = f.toarray()
        real = preprocessing.scale(f.toarray())
        #print real.shape

        pca = PCA(n_components=2)
        vals = pca.fit_transform(real)
        #print vals
        #print vals[0]

        # perform t-SNE embedding
        #vis_data = bh_sne(real)

        # plot the result
        #vis_x = vis_data[:, 0]
        #vis_y = vis_data[:, 1]

        #x = vis_x.reshape(len(vis_x),1)
        #y = vis_y.reshape(len(vis_y),1)
        x1 = map(lambda x: x[0],vals)
        y1 = map(lambda x: x[1],vals)

        #print x1
        #print y1

        print "done embed..."

        return zip(map(lambda x: x[0],Sites),x1,y1)

    def google_scrape(term,mapping,urls_to_content):
        print "running scrape..."
        term = urllib.unquote(term)
        print "Google searching:" + term
        urls = []
        for url in search(term, stop=10):
            if url in urls_to_content:
                urls.append((url,urls_to_content[url],"TEXT"))
                print "skipping...", url
                continue
            social_media = False
            for x in mapping:
                if url.startswith(x["urls"][0]):
                    urls.append((url,x["site"],"SOCIAL"))
                    social_media = True
                    break
            if not social_media:
                #print tldextract.extract(url).domain
                try:
                    response = urllib2.urlopen(url)
                    html = response.read()
                    soup = BeautifulSoup(html, "lxml")
                    text = soup.get_text()
                    urls.append((url,text,"TEXT"))
                    urls_to_content[url] = text
                except urllib2.HTTPError:
                    print "ERROR"
                    urls.append((url,"","TEXT"))
                    urls_to_content[url] = text
                #print html2text.html2text(html)
                #doc = nlp(text)
        print "done scrape..."
        return urls
    def connected():
        print "Connected!"

    my = MyHandler
    server = HTTPServer(("localhost", 8080), my)
    server.url_dict = {}
    server.nlp = spacy.load('en')
    server.google_scrape = google_scrape
    server.urls_to_content = {}
    server.embed = embed
    server.social_mappings = social_mappings
    server.lights_search = lights_search
    server.terms_hash = {}
    server.socketIO = SocketIO('localhost', 3000, LoggingNamespace)
    server.socketIO.on('connect',connected)
    server.socketIO.on('disconnect',connected)
    server.socketIO.on('reconnect',connected)
    print "Server running..."
    server.serve_forever()
    print "Socket running..."
    server.socketIO.wait()
