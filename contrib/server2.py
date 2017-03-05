from flask import Flask, request, Response
from socketIO_client import SocketIO, LoggingNamespace
from json import loads, dumps
from datetime import datetime
from google import search
import time
import urlparse
from bs4 import BeautifulSoup
from sklearn.feature_extraction import FeatureHasher
from sklearn import preprocessing
from tsne import bh_sne
from nltk.tokenize import word_tokenize
import urlparse

import requests

import spacy
import re
import html2text
import tldextract
from sklearn.decomposition import PCA

from elasticsearch import Elasticsearch
import codecs
import sys

app = Flask(__name__)

# Social Sites
social_mappings = [{"site":"LINKEDIN","urls":["https://www.linkedin.com/in/"]},
    {"site":"INSTAGRAM","urls":["https://www.instagram.com/"]},
    {"site":"GITHUB","urls":["https://github.com/"]},
    {"site":"PINTEREST","urls":["https://www.pinterest.com/"]},
    {"site":"INSTAGRAM","urls":["https://www.instagram.com/"]},
    {"site":"FACEBOOK","urls":["https://www.facebook.com/"]},
    {"site":"TWITTER","urls":["https://twitter.com/"]},
    {"site":"F6S","urls":["https://www.f6s.com/"]}
    ]

url_dict = {}
terms_hash = {}
nlp = spacy.load('en')
urls_to_content = {}

action_count = 0

socketIO = SocketIO('localhost', 3000, LoggingNamespace)


# Called when a prompt is answered
@app.route('/answer/', methods=['GET'])
def handle_answer():
    print "GET: Answer"
    print request.args.get("id"), request.args.get("response")
    resp = Response(dumps({"ok":"cool"}))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

# Called when something is unliked
@app.route('/unlike/', methods=['GET'])
def handle_unlike():
    print "GET: Unlike"
    print request.args.get("id")
    resp = Response(dumps({"ok":"cool"}))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

# Called when clear is clicked
@app.route('/clear/', methods=['GET'])
def handle_clear():
    print "GET: Clear"
    resp = Response(dumps({"ok":"cool"}))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


# Called when reload is clicked
@app.route('/reload/', methods=['GET'])
def handle_reload():
    print "GET: Reload"
    resp = Response(dumps({"ok":"cool"}))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

# Called when save/export is clicked
@app.route('/save_export/', methods=['GET'])
def handle_save():
    print "GET: Save"
    resp = Response(dumps({"ok":"cool"}))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


# Called when any user browser movement occurs.
@app.route('/browser_action/', methods=['POST'])
def handle_brower_action():
    print "POST: Browser Action", dumps(request.form)
    data = request.form.to_dict()
    date = datetime.utcfromtimestamp(int(data["time"]) / 1000.)
    data["time"] = date.isoformat("T").split(".")[0]
    del data["key"]

    global action_count

    action_count += 1

    print "ACTION COUNT:", action_count

    if action_count % 10 == 0:
        socketIO.emit('prompt',dumps(
            {"question":"Is this person of interest?",
            "id":"q"+str(action_count),
            "image_url":"https://instagram.fphl1-1.fna.fbcdn.net/t51.2885-19/11371180_804405839674055_1031223292_a.jpg",
            "page_url":None}
            )
        )
        action_count += 1

    if action_count % 20 == 0:
        socketIO.emit('prompt',dumps(
            {"question":"Is this page relevant?",
            "id":"q"+str(action_count),
            "image_url":None,
            "page_url":"https://reviews.birdeye.com/virginia-dental-care-691679936"}
            )
        )
        action_count += 1

    # If it's a site or movement we don't care about, do nothing
    if data["url"] == None or data["url"] == "" or data["url"].startswith("http://localhost:3000/") or \
    data["url"] == "chrome://newtab/" or data["url"] == "chrome://extensions/" or \
    data["url"].startswith("https://mail.google.com/"):
        return "ok"

    # If it's a social site...
    if any(map(data["url"].startswith,map(lambda x: x["urls"][0],social_mappings))):
        print "--Social--"
        socketIO.emit('social_media',dumps({"account":data["url"]}))
        return "ok"

    # If it's a google search...
    elif data["url"].startswith("https://www.google.com/search") or \
    data["url"].startswith("https://www.google.com/webhp"):
        print "--Google Search--"

        parsed = urlparse.urlparse(data["url"])
        if 'q' in urlparse.parse_qs(parsed.query):
            q = urlparse.parse_qs(parsed.query)['q']
        else:
            try:
                q = data["url"].split("#q=")[1].split("&")[0]
            except IndexError:
                print "---No search term found---"
                return "ok"
        print "Query ->", q
        socketIO.emit('google_search',dumps({"q":q, "id":"g"+str(action_count)}))
        #urls = self.server.google_scrape(q,self.server.social_mappings,self.server.urls_to_content)
        #embedding = self.server.embed(urls)
        #embed_json = map(lambda x: {"url":x[0],"x":x[1],"y":x[2]},embedding)
        #print dumps(embed_json)
        # LIGHTS search hold off for now
        #results = lights_search(q)
        #self.server.socketIO.emit("dark_search",results)
        #self.server.socketIO.emit('google',dumps(embed_json))
        return "ok"


    elif data["url"] not in url_dict:
        print "New URL ->", data["url"]
        text = do_webpage(data["url"])
        url_dict[data["url"]] = {"url":data["url"], "text":None,"total_time":None,"count":1,"id":"p"+str(len(url_dict))}
        socketIO.emit('new_page',dumps(url_dict[data["url"]]))
        socketIO.emit('terms',dumps(rank_terms(text)))
        '''
            TODO:
            1) check what site it is...if google..do look ahead
            2) otherwise...download html..parse out stuff...
            3) supply option to check out entire domain?
            4) deep search, passive search
            5) run featurization, update embeding..display
        '''
    elif data["url"] in url_dict:
        print "Old URL ->", data["url"]
        url_dict[data["url"]]["count"] += 1
        socketIO.emit('old_page',dumps(url_dict[data["url"]]))


    # if we get here, return ok
    return "ok"

def rank_terms(text):
    all_ents = {}
    doc = nlp(text)
    for ent in doc.ents:
        t = ent.text.strip()
        all_ents[t] = all_ents.get(t,[])
        all_ents[t].append((ent.label))
        final_d = sorted(all_ents.iteritems(), key=lambda (k,v): (len(v),k), reverse=True)

    return {"terms":[{"term":key,"count":len(value)} for key,value in final_d][:10]}

def do_webpage(url):
    response = requests.get(url)
    html = response.text
    soup = BeautifulSoup(html, "lxml")
    data = soup.findAll(text=True)
    result = filter(visible, data)
    text = " ".join(result)
    return text

def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title']:
        return False
    elif re.match('<!--.*-->', str(element.encode('utf-8'))):
        return False
    return True

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
                response = requests.get(url)
                html = response.text
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

if __name__ == "__main__":
    app.debug=True
    app.run(threaded=True,
        host="0.0.0.0",
        port=(5000))