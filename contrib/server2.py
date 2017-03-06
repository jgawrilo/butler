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
import urllib2

import requests
import urllib

import spacy
import re
import html2text
import tldextract
from sklearn.decomposition import PCA

from elasticsearch import Elasticsearch
import codecs
import sys
import numpy as np

import os

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

prompts = {}
socials = {}

action_count = 0

name = ""

socketIO = SocketIO('localhost', 3000, LoggingNamespace)

success = {"success":True}


# Called when a prompt is answered
@app.route('/name/', methods=['GET'])
def handle_name():
    print "GET: Name"
    global name
    name = request.args.get("name")
    resp = Response(dumps(success))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

# Called when a prompt is answered
@app.route('/answer/', methods=['GET'])
def handle_answer():
    print "GET: Answer"
    print request.args.get("id"), request.args.get("response")
    resp = Response(dumps(success))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

# Called when something is unliked
@app.route('/unlike/', methods=['GET'])
def handle_unlike():
    print "GET: Unlike"
    print request.args.get("id")
    resp = Response(dumps(success))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

# Called when clear is clicked
@app.route('/clear/', methods=['GET'])
def handle_clear():
    print "GET: Clear"
    resp = Response(dumps(success))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


# Called when reload is clicked
@app.route('/reload/', methods=['GET'])
def handle_reload():
    print "GET: Reload"
    resp = Response(dumps(success))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

# Called when save/export is clicked
@app.route('/save_export/', methods=['GET'])
def handle_save():
    print "GET: Save"
    resp = Response(dumps(success))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp


# Called when any user browser movement occurs.
@app.route('/browser_action/', methods=['POST'])
def handle_brower_action():
    global action_count
    action_count += 1

    data = request.form.to_dict()
    date = datetime.utcfromtimestamp(int(data["time"]) / 1000.)
    data["time"] = date.isoformat("T").split(".")[0]
    del data["key"]

    print name, action_count, "POST: Action", data["time"], data["url"]

    # Fake data stub for now
    if action_count % 5 == 0:
        pid = "q"+str(len(prompts))
        p = {
                "question":"Is this picture of interest?",
                "id":pid,
                "image_url":"https://lh3.googleusercontent.com/-8kuDJO1frwY/AAAAAAAAAAI/AAAAAAAAATk/G8U8sX7PvcU/s120-p-rw-no/photo.jpg",
                "page_url":None
        }
        socketIO.emit('prompt',dumps(p))
        prompts[pid] = p

    if action_count % 10 == 0:
        pid = "q"+str(len(prompts))
        p = {
                "question":"Is this page relevant?",
                "id":pid,
                "image_url":None,
                "page_url":"https://reviews.birdeye.com/virginia-dental-care-691679936"
        }
        socketIO.emit('prompt',dumps(p))
        prompts[pid] = p


    # If it's a site or movement we don't care about, do nothing
    if data["url"] == None or data["url"] == "" or data["url"].startswith("http://localhost:3000/") or \
    data["url"] == "chrome://newtab/" or data["url"] == "chrome://extensions/" or \
    data["url"].startswith("https://mail.google.com/"):
        return "nothing"

    # If it's a social site...
    if any(map(data["url"].startswith,map(lambda x: x["urls"][0],social_mappings))):
        if data["url"] not in url_dict:
            print "-- Social-- "
            sid = "sm"+str(len(socials))
            sm = {
                "id":sid,
                "site":"Instagram",
                "url":data["url"],
                "account":"juddydotg",
                "image_url":"https://instagram.fphl1-1.fna.fbcdn.net/t51.2885-19/11371180_804405839674055_1031223292_a.jpg",
                "name":"Justin Gawrilow",
                "profile_snippet":"Fitter,happier more productive",
                "relevance_score":0.0
            }
            socketIO.emit('social_media',dumps(sm))
            socials[sid] = sm
            #new_url(data["url"],False)
            return "ok"
        else:
            print "Old URL ->", data["url"]

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
        socketIO.emit('google_search',dumps({"url":data["url"],"query":q, "id":"g"+str(action_count)}))
        urls = google_scrape(q)
        embedding = embed(urls)
        #print dumps(embedding,indent=2)
        # LIGHTS search hold off for now
        #results = lights_search(q)
        #self.server.socketIO.emit("dark_search",results)
        print dumps({"data":embedding},indent=2)
        socketIO.emit('page_update',dumps({"data":embedding}))
        return "ok"


    elif data["url"] in url_dict:
        print "Old URL ->", data["url"]
        url_dict[data["url"]]["view_count"] += 1

    # If it's a new site...
    elif data["url"] not in url_dict:
        new_url(data["url"])


    # if we get here, return ok
    return "ok"

def new_url(url,send_to_client=True):
    print "-- New Page --"
    pid = "page" + str(len(url_dict))
    screen_shot_loc = "screenshots/"+pid+".png"
    text = do_webpage(url,pid,True)

    urls_to_content[url] = text

    page = {
            "url":url,
            "screen_shot_url":screen_shot_loc,
            "view_time_seconds":None,
            "view_count":1,
            "classification":"news",
            "viewed":True,
            "id":pid,
            "x":None,
            "y":None,
            "relevance_score":0.5
    }

    print "adding", url, "to dict"
    url_dict[url] = page

    if send_to_client:
        socketIO.emit('new_page',dumps(url_dict[url]))

        terms = rank_terms(text)
        #print dumps(terms,indent=2)
        socketIO.emit('terms',dumps(terms))
    '''
        TODO:
        1) check what site it is...if google..do look ahead
        2) otherwise...download html..parse out stuff...
        3) supply option to check out entire domain?
        4) deep search, passive search
        5) run featurization, update embeding..display
    '''

def rank_terms(text):
    all_ents = {}
    doc = nlp(text)
    i = len(terms_hash)
    for ent in doc.ents:
        t = ent.text.strip()
        terms_hash[t] = i
        i += 1
        all_ents[t] = all_ents.get(t,[])
        all_ents[t].append((ent.label))
        final_d = sorted(all_ents.iteritems(), key=lambda (k,v): (len(v),k), reverse=True)

    return {"terms":[{"term":key,"count":len(value),
              "id":"t"+str(terms_hash[key]),
              "classification":"unknown",
              "relevance_score":0.8} for key,value in final_d][:10]}

def do_webpage(url,pid,screenshot=True):
    # Take screenshot of page
    if screenshot:
        os.system("python screenshot.py " + url + " " + pid + ".png")
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
    print "Running embedding"
    D = []
    Socials = []
    Sites = []
    dSet = set()
    for (page_obj,text,site_type) in data:
        if site_type == "TEXT":
            letters = {}
            words = word_tokenize(text)
            for char in words:
                letters[char] = letters.get(char,0) + 1
                dSet.add(char)
            D.append(letters)
            Sites.append((page_obj,text,site_type))
        else:
            Socials.append((page_obj,text,site_type))
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

    def joinit(x):
        obj,x,y = x
        print obj
        print x
        print y
        print obj[0]
        obj[0]["x"] = x
        obj[0]["y"] = y
        return obj[0]

    return map(joinit,zip(Sites,x1,y1))

"""
{
            "url":"https://registry.theknot.com/hilary-swab-justin-gawrilow-may-2013-dc/433269",
            "screen_shot_url":"screenshots/p44.png",
            "view_time_seconds":15,
            "view_count":1,
            "classification":"news",
            "viewed":false,
            "id":"p44",
            "x":14.534,
            "y":19.345,
            "relevance_score":0.0
        }
"""
def google_scrape(term):

    # check urls against what the user has already gone to.


    global urls_to_content
    term = urllib.unquote(term)
    print "Google searching:" + term
    urls = []
    for url in search(term, stop=5):
        if url in urls_to_content:
            urls.append((url,urls_to_content[url],"TEXT"))
            continue
        social_media = False
        for x in social_mappings:
            if url.startswith(x["urls"][0]):
                urls.append((url,x["site"],"SOCIAL"))
                social_media = True
                break
        if not social_media:
            try:
                pid = "page" + str(len(url_dict))
                screen_shot_loc = "screenshots/"+pid+".png"
                text = do_webpage(url,pid,screenshot=False)

                page = {
                        "url":url,
                        "screen_shot_url":screen_shot_loc,
                        "view_time_seconds":None,
                        "view_count":0,
                        "classification":np.random.choice(['news','articles','social','dark web','info','stalker'],1)[0],
                        "viewed":False,
                        "id":pid,
                        "x":None,
                        "y":None,
                        "relevance_score":0.5
                }

                url_dict[url] = page
                urls.append((page,text,"TEXT"))
                urls_to_content[url] = text
            except urllib2.HTTPError:
                page = {
                        "url":url,
                        "screen_shot_url":screen_shot_loc,
                        "view_time_seconds":None,
                        "view_count":0,
                        "classification":np.random.choice(['news','articles','social','dark web','info','stalker'],1)[0],
                        "viewed":False,
                        "id":pid,
                        "x":None,
                        "y":None,
                        "relevance_score":0.5
                }
                print "ERROR"
                urls.append((page,"","TEXT"))
                urls_to_content[url] = text
    print "Done Google searching..."
    return urls

if __name__ == "__main__":
    app.debug=True
    app.run(threaded=True,
        host="0.0.0.0",
        port=(5000))