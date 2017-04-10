# -*- coding: utf-8 -*-

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
#from tsne import bh_sne
from nltk.tokenize import word_tokenize
import nltk
import urlparse
import urllib2

import requests
import urllib

from subprocess import Popen
from sys import stderr

from goose import Goose

import spacy
import re
import html2text
from sklearn.decomposition import PCA

from elasticsearch import Elasticsearch
import codecs
import sys
import numpy as np

reload(sys)
sys.setdefaultencoding('utf-8')

import networkx as nx

es = Elasticsearch(["localhost:9200"])

import os

app = Flask(__name__)

from OpenSSL import SSL

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


# Social Sites
social_mappings = [
    #{"site":"LinkedIn","urls":["https://www.linkedin.com/"]},
    {"site":"Instagram","urls":["https://www.instagram.com/"],"left_split":"https://www.instagram.com/",
    "profile_class":"_79dar","image_class":"_iv4d5"},
    {"site":"Github","urls":["https://github.com/"],"left_split":"https://github.com/"},
    {"site":"Pinterest","urls":["https://www.pinterest.com/"],"left_split":"https://www.pinterest.com/"},
    {"site":"Facebook","urls":["https://www.facebook.com/"], "left_split":"https://www.facebook.com/"},
    {"site":"Twitter","urls":["https://twitter.com/"],"left_split":"https://twitter.com/"},
    {"site":"YouTube","urls":["https://www.youtube.com"],"left_split":"https://twitter.com/"}
    #{"site":"F6S","urls":["https://www.f6s.com/"]}
    ]

JAVA_BIN_PATH = 'java'
DOT_BIN_PATH = 'dot'
STANFORD_IE_FOLDER = 'stanford-openie'

url_dict = {}
terms_hash = {}
nlp = spacy.load('en')
urls_to_content = {}

prompts = {}
socials = {}

search_set = set()

action_count = 0

last_url = None

goosey = Goose()

name = "unknown"

socketIO = SocketIO('localhost', 3000, LoggingNamespace)

resp = Response(dumps({"success":True}))
resp.headers['Access-Control-Allow-Origin'] = '*'

def getInstaData(text):
    lines = text.split("\n")
    for line in lines:
        if "window._sharedData =" in line:
            data = loads(line.split("window._sharedData =")[1].split(";</script>")[0])
            break
    return data

# Called when twitter is scraped...
@app.route('/youtube/', methods=['GET'])
def handle_youtube():
    global name
    print "GET: Youtube"
    handle = request.args.get("handle")
    print handle
    os.system("python mine_youtube.py " + handle + " " + "./saves/"+name+"/")
    return resp

# Called when twitter is scraped...
@app.route('/twitter/', methods=['GET'])
def handle_twitter():
    global name
    print "GET: Twitter"
    handle = request.args.get("handle")
    print handle
    os.system("python mine_twitter.py " + handle + " " + "./saves/"+name+"/ " + name)
    return resp

# Called when instagram is scraped...
@app.route('/instagram/', methods=['GET'])
def handle_instagram():
    global name
    print "GET: Instagram"
    handle = request.args.get("handle")
    print handle
    os.system("python mine_insta.py " + handle + " " + "./saves/"+name+"/")
    return resp


# Called when a name is given
@app.route('/name/', methods=['GET'])
def handle_name():
    print "GET: Name"
    global name
    name = request.args.get("name")
    os.system("mkdir -p ./saves/"+name)
    return resp

# Called when a prompt is answered
@app.route('/answer/', methods=['GET'])
def handle_answer():
    print "GET: Answer"
    print request.args.get("id"), request.args.get("response")
    return resp

# Called when something is unliked
@app.route('/unlike/', methods=['GET'])
def handle_unlike():
    print "GET: Unlike"
    print request.args.get("id")
    return resp

# Called when clear is clicked
@app.route('/clear/', methods=['GET'])
def handle_clear():
    global name, url_dict, terms_hash, socials, urls_to_content, prompts, socials
    global action_count, last_url

    name = "unknown"
    url_dict = {}
    terms_hash = {}
    urls_to_content = {}
    prompts = {}
    socials = {}
    action_count = 0
    last_url = None


    print "GET: Clear"
    return resp


# Called when reload is clicked
@app.route('/reload/', methods=['GET'])
def handle_reload():
    global name, url_dict, terms_hash, socials, urls_to_content, prompts, socials
    print "GET: Reload"

    name = request.args.get("name")
    with codecs.open("./saves/" + name + "/butler_data.json","r",encoding="utf8") as ip:
        data_dump = loads(ip.read())
        url_dict = data_dump["urls"]
        terms_hash = data_dump["terms"]
        socials = data_dump["social"]
        urls_to_content = data_dump["urls_to_content"]

    print len(url_dict)
    return resp

# Called when save/export is clicked
@app.route('/save_export/', methods=['GET'])
def handle_save():
    global name
    global url_dict, terms_hash, socials
    data_dump = {"urls":url_dict,"terms":terms_hash,"social":socials,"urls_to_content":urls_to_content}
    print "GET: Save"
    with codecs.open("./saves/" + name + "/butler_data.json","w",encoding="utf8") as output:
        output.write(dumps(data_dump,indent=2))

    return resp

def do_social(url):
    url = url.split("?")[0]
    surl = None
    for s in social_mappings:
        if url.startswith(s["urls"][0]):
            surl = s
            break

    if url not in url_dict:
        print "-- Social-- "
        new_url(url,False,False,"Social")
        sid = "sm"+str(len(socials))
        response = requests.get(url)

        if surl["site"] == "Instagram":
            d = getInstaData(response.text)
            pname = d["entry_data"]["ProfilePage"][0]["user"]["full_name"]
            pic = d["entry_data"]["ProfilePage"][0]["user"]["profile_pic_url"]
            bio = d["entry_data"]["ProfilePage"][0]["user"]["biography"]
        elif surl["site"] == "Twitter":
            html = response.text
            soup = BeautifulSoup(html, "lxml")
            print "ProfileHeaderCard-nameLink u-textInheritColor js-nav" in html
            prof = soup.findAll(class_="ProfileHeaderCard-nameLink")
            print prof
            img = soup.findAll("img", { "class" : "ProfileAvatar-image " })
            pname = prof[0].contents[0]
            pic = img[0]["src"]
        else:
            pic = "img/unknown.png"
            pname =""

        sm = {
            "id":sid,
            "site":surl["site"],
            "url":url,
            "account":url.split(surl["left_split"])[1].split("?")[0],
            "image_url":pic,
            "name":pname,
            "profile_snippet":"",
            "relevance_score":0.0
        }
        socketIO.emit('social_media',dumps(sm))
        socials[sid] = sm
        #
        return resp
    else:
        print "-- Social-- "
        print "Old URL ->", url
        return resp

def createGraph(data):
    nodes = set()
    edges = {}

    for d in data:
        url = d["url"].strip()
        nodes.add((url,"URL"))
        for e in d["entities"]:
            n = e["ent"].strip().replace("\t"," ").replace("\n"," ").lower()
            if n != "":
                nodes.add((n,"ENT"))
                edges[n] = edges.get(n,{})
                edges[n][url] = 1
        '''
        for e in d["relationships"]:
            n = e["one"].strip().replace("\t"," ").replace("\n"," ").lower()
            if n != "":
                nodes.add((n,"REL1"))
                edges[n] = edges.get(n,{})
                edges[n][url] = 1
        '''

    with codecs.open("nodes.txt","w",encoding="utf8") as nodeout:
        nodeout.write("Id\tType\n")
        for n in nodes:
            nodeout.write(n[0].decode("utf8","ignore").encode("utf8","ignore") + "\t" + n[1].decode("utf8","ignore").encode("utf8","ignore") + "\n")

    with codecs.open("edges.txt","w",encoding="utf8") as edgeout:
        edgeout.write("Source\tTarget\tWeight\n")
        for a in edges:
            for b in edges[a]:
                edgeout.write(a.decode("utf8","ignore").encode("utf8","ignore") + "\t" + b.decode("utf8","ignore").encode("utf8","ignore") + "\t" + "1\n")



@app.route('/mysearch/',methods=["GET"])
def handle_mysearch():
    q = request.args.get("q")
    with codecs.open("profiles.json","r",encoding="utf8") as ip:
        data_dump = loads(ip.read())
        print dumps(data_dump)
        resp = Response(dumps(data_dump))
        resp.headers['Access-Control-Allow-Origin'] = '*'
        socketIO.emit('google_search',dumps(data_dump))
        return resp


# here I define a tokenizer and stemmer which returns the set of stems in the text that it is passed
# Punkt Sentence Tokenizer, sent means sentence 
def tokenize_and_stem(text):
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    from nltk.stem.snowball import SnowballStemmer
    stemmer = SnowballStemmer("english")
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    stems = [stemmer.stem(t) for t in filtered_tokens]
    return stems

@app.route('/search/', methods=["GET"])
def handle_search():
    global action_count
    global last_url
    global search_set

    q = request.args.get("q")
    n = int(request.args.get("n","20"))
    print "Query ->", q
    if q in search_set:
        print "Already searched..."
        return resp
    search_set.add(q)
    #socketIO.emit('google_search',dumps({"url":data["url"],"query":q, "id":"g"+str(action_count)}))
    urls = google_scrape(q,n)

    g = nx.Graph()

    # Note that the result of this block takes a while to show
    from sklearn.feature_extraction.text import TfidfVectorizer
    

    #define vectorizer parameters
    tfidf_vectorizer = TfidfVectorizer(max_df=0.8, max_features=200000,
                                     min_df=0.1, stop_words='english',
                                     use_idf=True, tokenizer=tokenize_and_stem, ngram_range=(1,3))

    
    #bet = nx.betweenness_centrality(g)
    #partition = community.best_partition(g)

    #g.add_edge()

    #comps = nx.connected_components(g)
    #g.next()

    '''
    data = [{"url":x[0]["url"],"entities":[{"ent":ent.text, "type":ent.label_} 
    for ent in nlp(unicode(x[1])).ents]
    ,"relationships":[{"a":tt[0], "relation":tt[1], "b":tt[2]} 
    for tt in stanford_ie(x[1])]} for x in urls]
    '''

    data = [{"url":x[0]["url"],"entities":[{"ent":ent.text, "type":ent.label_} 
    for ent in nlp(unicode(x[1])).ents]} for x in urls]

    '''
        {
                    "id":"e1",
                    "type":"Date",
                    "value":"February of 2014",
                    "count":1,
                    "from":[
                        "https://www.corporationwiki.com/p/2ekibg/vladimir-kudyakov"
                    ]
                },
    '''
    entities = {}
    for d in data:
        for e in d["entities"]:
            entry = entities.get(e["ent"],{"id":"e"+str(len(entities)),
                "type":e["type"],
                "value":e["ent"],
                "count":0,
                "from":[]})
            entry["count"] += 1
            if d["url"] not in entry["from"]:
                entry["from"].append(d["url"])
            entities[e["ent"]] = entry

    ent_array = [entities[x] for x in entities if entities[x]["count"] > 1 or entities[x]["type"] in ["PERSON","LOC"]]

    print dumps(entities,indent=2)


    #createGraph(data)


    textx = [x[1] for x in urls]

    #rels = [{"a":tt[0], "relation":tt[1], "b":tt[2]} for tt in stanford_ie("\n".join([x[1] for x in urls]))]
    rels = []
    tfidf_matrix = tfidf_vectorizer.fit_transform(textx) #fit the vectorizer to synopses

    #print textx

    from sklearn.cluster import KMeans

    num_clusters = 3

    km = KMeans(n_clusters=num_clusters)

    km.fit(tfidf_matrix)

    clusters = km.labels_.tolist()
    print clusters

    resp = Response(dumps({"entities":ent_array,"relationships":rels}))
    resp.headers['Access-Control-Allow-Origin'] = '*'
    for i,url in enumerate(urls):
        print i, url[0]["url"]
        with codecs.open("data/"+str(i)+"_fie.txt","w",encoding="utf8") as output:
            output.write(url[0]["url"])
        with codecs.open("data/"+str(i)+".txt","w",encoding="utf8") as output:
            output.write(url[1])
        with codecs.open("data/"+str(i)+"_goose.txt","w",encoding="utf8") as output:
            output.write(url[2])
        with codecs.open("data/"+str(i)+"_data.txt","w",encoding="utf8") as output:
            output.write(dumps(data[i],indent=2))

    #print stanford_ie(",".join(["data/"+str(i)+"_goose.txt" for i,x in enumerate(urls)]))
    return resp


# Called when any user browser movement occurs.
@app.route('/browser_action/', methods=['POST'])
def handle_brower_action():
    global action_count
    global last_url
    global search_set
    action_count += 1

    data = request.form.to_dict()
    date = datetime.utcfromtimestamp(int(data["time"]) / 1000.)
    data["time"] = date.isoformat("T").split(".")[0]
    del data["key"]

    print "NAME:",name, "ACTIONS:", action_count, data["time"], data["url"], "LAST:", last_url

    if action_count % 7 == 0:
        do_terms()
    # Fake data stub for now
    '''
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
    # END of stubs ##################
    '''


    # If it's a site or movement we don't care about, do nothing
    if data["url"] == None or data["url"] == "" or data["url"].startswith("http://localhost:3000/") or \
    data["url"] == "chrome://newtab/" or data["url"] == "chrome://extensions/" or \
    data["url"].startswith("https://mail.google.com/") or data["url"].startswith("https://docs.google.com/") \
    or data["url"].startswith("https://localhost:5000"):
        # Change time of last URL
        if last_url != None:
            view_time = int(time.mktime(datetime.now().timetuple())) - url_dict[last_url]["last_seen"]
            url_dict[last_url]["view_time_seconds"] += view_time
            url_dict[last_url]["last_seen"] = int(time.mktime(datetime.now().timetuple()))
            print last_url, "was viewed", url_dict[last_url]["view_time_seconds"]
            socketIO.emit('new_page',dumps(url_dict[last_url]))
        last_url = None
        return resp

    # If it's a social site...
    if any(map(data["url"].startswith,map(lambda x: x["urls"][0],social_mappings))):
        return do_social(data["url"])

    # If it's a google search...
    elif data["url"].startswith("https://www.google.com/search") or \
    data["url"].startswith("https://www.google.com/webhp"):
        print "--Google Search--"

        parsed = urlparse.urlparse(data["url"])
        if 'q' in urlparse.parse_qs(parsed.query):
            q = urlparse.parse_qs(parsed.query)['q'][0].strip()
        else:
            try:
                q = data["url"].split("#q=")[1].split("&")[0].strip()
            except IndexError:
                print "---No search term found---"
                return resp
        print "Query ->", q
        if q in search_set:
            print "Already searched..."
            return resp
        search_set.add(q)
        socketIO.emit('google_search',dumps({"url":data["url"],"query":q, "id":"g"+str(action_count)}))
        urls = google_scrape(q)

        for i,url in enumerate(urls):
            with codecs.open("data/"+str(i)+".txt","w",encoding="utf8") as output:
                output.write(url[1])
            with codecs.open("data/"+str(i)+"_goose.txt","w",encoding="utf8") as output:
                output.write(url[2])

        #print stanford_ie(",".join(["data/"+str(i)+"_goose.txt" for i,x in enumerate(urls)]))

        embedding = embed(urls)
        #print dumps(embedding,indent=2)
        # LIGHTS search hold off for now
        #results = lights_search(q)
        #self.server.socketIO.emit("dark_search",results)
        print dumps({"data":embedding},indent=2)
        socketIO.emit('page_update',dumps({"data":embedding}))
        return resp


    # If it's an old site...
    elif data["url"] in url_dict and url_dict[data["url"]]["viewed"]:
        new_url(data["url"],True,False,"Unknown")
        return resp

    # If it's a new site...
    elif data["url"] not in url_dict or not url_dict[data["url"]]["viewed"]:
        new_url(data["url"],True,False,"Unknown")
        return resp


    # if we get here, return ok
    return resp

def process_entity_relations(entity_relations_str, verbose=True):
    # format is ollie.
    entity_relations = list()
    for s in entity_relations_str:
        entity_relations.append(s[s.find("(") + 1:s.find(")")].split(';'))
    return entity_relations
'''
def stanford_ie(text, verbose=True, generate_graphviz=False):
    input_filename = "data/data.txt"
    with codecs.open("data/data.txt","w",encoding="utf8") as output:
        output.write(text) 
    out = 'out.txt'
    input_filename = input_filename.replace(',', ' ')

    new_filename = ''
    for filename in input_filename.split():
        if filename.startswith('/'):  # absolute path.
            new_filename += '{} '.format(filename)
        else:
            new_filename += '../{} '.format(filename)

    absolute_path_to_script = os.path.dirname(os.path.realpath(__file__)) + '/'
    command = 'cd {};'.format(absolute_path_to_script)
    command += 'cd {}; {} -mx12g -cp "stanford-openie.jar:stanford-openie-models.jar:lib/*" ' \
               'edu.stanford.nlp.naturalli.OpenIE {} -format ollie > {}'. \
        format(STANFORD_IE_FOLDER, JAVA_BIN_PATH, new_filename, "../"+out)

    if verbose:
        java_process = Popen(command, stdout=stderr, shell=True)
    else:
        java_process = Popen(command, stdout=stderr, stderr=open(os.devnull, 'w'), shell=True)
    java_process.wait()
    assert not java_process.returncode, 'ERROR: Call to stanford_ie exited with a non-zero code status.'

    with open(out, 'r') as output_file:
        results_str = output_file.readlines()
    #os.remove(out)

    results = process_entity_relations(results_str, verbose)
    if generate_graphviz:
        generate_graphviz_graph(results, verbose)

    return results
'''
def do_terms():
    global name
    soc = ""
    if name != "unknown":
        try:
            res = es.search(index=name, body={"query": {"match_all": {}}})
            soc = " ".join([x["_source"]["text"] for x in res["hits"]["hits"]])
        except:
            soc = ""
    global urls_to_content
    if urls_to_content:
        text = "\n".join(urls_to_content.values()) + soc
    else:
        text = soc
    if text != "":
        terms = rank_terms(text)
        socketIO.emit('terms',dumps(terms))

def new_url(url,send_to_client=True,screenshot=True,page_type=None):
    global last_url
    # Change time of last URL
    if last_url != None:
        view_time = int(time.mktime(datetime.now().timetuple())) - url_dict[last_url]["last_seen"]
        url_dict[last_url]["view_time_seconds"] += view_time
        url_dict[last_url]["last_seen"] = int(time.mktime(datetime.now().timetuple()))
        socketIO.emit('new_page',dumps(url_dict[last_url]))

    last_url = url
    
    if url not in url_dict:
        print "-- New Page --"
        pid = "page" + str(len(url_dict))
        screen_shot_loc = "screenshots/"+pid+".png"
        page = {
            "url":url,
            "screen_shot_url":screen_shot_loc,
            "view_time_seconds":0,
            "last_seen":int(time.mktime(datetime.now().timetuple())),
            "view_count":1,
            "classification":page_type,
            "viewed":True,
            "id":pid,
            "x":None,
            "y":None,
            "relevance_score":None
        }
        print "adding", url, "to dict"
        url_dict[url] = page
        
        # This may error out
        text = do_webpage(url,pid,screenshot)
        urls_to_content[url] = text
        
    else:
        print "-- Old Page -- Updating..."
        pid = url_dict[url]["id"]
        screen_shot_loc = url_dict[url]["screen_shot_url"]
        text = urls_to_content[url]
        url_dict[url]["view_count"] += 1
        url_dict[url]["viewed"] = True
        url_dict[url]["last_seen"] = int(time.mktime(datetime.now().timetuple()))

    if send_to_client:
        socketIO.emit('new_page',dumps(url_dict[url]))
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

    div = sum([len(value) for key,value in final_d][:20])

    return {"terms":[{"term":key,"count":len(value),
              "id":"t"+str(terms_hash[key]),
              "classification":"unknown",
              "relevance_score":str(1-float(len(value))/div)[1:4]} for key,value in final_d][:20]}

def do_webpage(url,pid,screenshot=False):
    # Take screenshot of page
    if screenshot:
        os.system("python screenshot.py " + url + " " + pid + ".png")
    headers = headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(url,headers=headers)
    html = response.content
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
    for (page_obj,text) in data:
        letters = {}
        words = word_tokenize(text)
        for char in words:
            letters[char] = letters.get(char,0) + 1
            dSet.add(char)
        D.append(letters)
        Sites.append((page_obj,text))

    h = FeatureHasher(n_features=len(dSet))
    f = h.transform(D)
    df = f.toarray()
    real = preprocessing.scale(f.toarray())

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

def google_scrape(term,num_pages=10):

    dontdo = [
        "http://www.whitepages.com/name/Vladimir-Khudyakov",
        "https://www.broward.county-taxes.com/public/real_estate/parcels/514110-18-1560/bills/10368915",
        "http://search.sunbiz.org/Inquiry/CorporationSearch/ConvertTiffToPDF?storagePath=COR%5C2014%5C1021%5C64887563.Tif&documentNumber=L13000041221",
        "http://www.peekyou.com/vladimir_gudkov",
        "https://photographylife.com/sigma-does-it-again-4-new-lenses-announced/",
        "https://en.wikipedia.org/wiki/Oprichnina",
        "http://www.iccabs.org/2011/committees/",
        "http://search.sunbiz.org/Inquiry/CorporationSearch/SearchResultDetail?inquirytype=OfficerRegisteredAgentName&directionType=Initial&searchNameOrder=ORANDAN%20L130000412213&aggregateId=flal-l13000041221-985b5cf7-acd1-4d7f-872a-30ff1a2694a3&searchTerm=Oranburg%2C%20Philip%20Reid&listNameOrder=ORANBURGPHILIPREID%20H683070",
        "https://apkpure.co/sunny-isles-beach-fl-miami/"
    ]

    global urls_to_content
    term = urllib.unquote(term)
    print "Google searching:" + term
    urls = []
    i = 1
    for url in search(term, stop=num_pages):
        print url, i
        
        if any(map(url.startswith,map(lambda x: x["urls"][0],social_mappings))) or \
        url.endswith(".pdf") or url in dontdo:
            print "Skipping!!!"
            #do_social(url)
            continue
        if url in urls_to_content:
            urls.append((url_dict[url],urls_to_content[url])    )
            continue
        try:
            pid = "page" + str(len(url_dict))
            screen_shot_loc = "screenshots/"+pid+".png"
            text = do_webpage(url,pid,screenshot=False)

            article = goosey.extract(url=url)

            page = {
            "url":url,
            "screen_shot_url":screen_shot_loc,
            "view_time_seconds":0,
            "view_count":0,
            "classification":"Unknown",
            "viewed":False,
            "id":pid,
            "x":None,
            "y":None,
            "relevance_score":None
            }

            url_dict[url] = page
            urls.append((page,text,article.cleaned_text))
            urls_to_content[url] = text
            i += 1

        except:
            print "ERROR on:", url
            page = {
                    "url":url,
                    "screen_shot_url":screen_shot_loc,
                    "view_time_seconds":0,
                    "view_count":0,
                    "classification":"Unknown",
                    "viewed":False,
                    "id":pid,
                    "x":None,
                    "y":None,
                    "relevance_score":None
            }
            
            urls.append((page,"",article.cleaned_text))
            urls_to_content[url] = text
    print "Done Google searching..."
    return urls

if __name__ == "__main__":
    app.debug=True
    context = ('server.crt', 'server.key')
    print "Running..."
    app.run(threaded=False,
        host="0.0.0.0",
        port=(5000), ssl_context=context)
