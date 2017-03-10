import requests
import json
import codecs, time
import sys

url = "https://www.instagram.com/query/"

headers = {
"accept":"*/*",
"accept-encoding":"gzip, deflate, br",
"accept-language":"en-US,en;q=0.8,es;q=0.6",
"content-length":1,
"content-type":"application/x-www-form-urlencoded",
"cookie":"csrftoken=OnaRti9X2BMY7UTGN1D9m6qOAPl0xMwT; s_network=""; ig_vw=1822; ig_pr=1.3333333730697632",
"origin":"https://www.instagram.com",
"referer":"https://www.instagram.com/abshik/",
"user-agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
"x-csrftoken":"OnaRti9X2BMY7UTGN1D9m6qOAPl0xMwT",
"x-instagram-ajax":1,
"x-requested-with":"XMLHttpRequest"
}



def getAccountData(handle,save_loc):
    output = codecs.open(save_loc + handle + ".json","w",encoding="utf8")
    images = []
    first_page = requests.get("https://www.instagram.com/" + handle)
    lines = first_page.text.split("\n")
    after_id = None
    for line in lines:
        if "window._sharedData =" in line:
            data = json.loads(line.split("window._sharedData =")[1].split(";</script>")[0])
            #print json.dumps(data,indent=2)
            images.extend(data["entry_data"]["ProfilePage"][0]["user"]["media"]["nodes"])
            #after_id = data["entry_data"]["ProfilePage"][0]["user"]["media"]["page_info"]["end_cursor"]
            #print data["entry_data"]["LocationsPage"][0]["location"]["media"]["count"]
            #print data["entry_data"]["LocationsPage"][0]["location"]["media"]["nodes"]
            #output.write("\n".join(map(json.dumps, data["entry_data"]["LocationsPage"][0]["location"]["media"]["nodes"])) + "\n")
            break
    #print after_id
    #print "AQAZZRVtj0KfOAkJCID_KhzLin_QgyVg_2tEPYMv7-0hwQR8tZHIrB_AA9F3k0mnYh-mT4g9oTZ7eNPeNnlkdQwNJ0CTVni8kHa0Z8JiXJINL9nPv8bMOUlWohVnRfLlqqY"

    handle_id = images[0]["owner"]["id"]

    go = True

    while go:
        after_id = images[-1]["id"]
        print after_id
        print len(images)
        #print "last_id", after_id

        q = "ig_user(" + handle_id + ") { media.after("+after_id+""", 12) {
          count,
          nodes {
            __typename,
            caption,
            code,
            comments {
              count
            },
            comments_disabled,
            date,
            dimensions {
              height,
              width
            },
            display_src,
            id,
            is_video,
            likes {
              count
            },
            owner {
              id
            },
            thumbnail_src,
            video_views
          },
          page_info
        }
         }"""

        data = {'q':q,
        'ref':'users::show',
        'query_id':None}

        #print q

        r = requests.post(url, data = data,headers=headers)
        #print r.text
        try:
            d = json.loads(r.text)
            #print json.dumps(d,indent=2)
        except ValueError as e:
            print r.text
            raise e
        time.sleep(1)
        if d["status"] == "fail":
            print "Sleeping a second"
            time.sleep(120)
        else:
            try:
                images.extend(d["media"]["nodes"])
                go = d["media"]["page_info"]["has_next_page"]
                output.write("\n".join(map(json.dumps,d["media"]["nodes"])) + "\n")
            except Exception:
                print json.dumps(d,indent=2)

def getLocationData(ig_location):
    output = codecs.open(ig_location + ".json","w",encoding="utf8")
    images = []
    first_page = requests.get("https://www.instagram.com/explore/locations/" + ig_location)
    lines = first_page.text.split("\n")
    for line in lines:
        if "window._sharedData =" in line:
            data = json.loads(line.split("window._sharedData =")[1].split(";</script>")[0])
            images.extend(data["entry_data"]["LocationsPage"][0]["location"]["media"]["nodes"])
            print data["entry_data"]["LocationsPage"][0]["location"]["media"]["count"]
            #print data["entry_data"]["LocationsPage"][0]["location"]["media"]["nodes"]
            output.write("\n".join(map(json.dumps, data["entry_data"]["LocationsPage"][0]["location"]["media"]["nodes"])) + "\n")
            break

    go = True
    

    while go:
        after_id = images[-1]["id"]
        print len(images)
        #print "last_id", after_id

        q = "ig_location(" + ig_location + ") { media.after(" +  after_id + """ , 20) {
          count,
          nodes {
            __typename,
            caption,
            code,
            location,
            comments {
              count,
              text
            },
            date,
            dimensions {
              height,
              width
            },
            display_src,
            id,
            is_video,
            likes {
              count
            },
            owner {
              id,
              username
            },
            thumbnail_src,
            video_views,
            location {
              latitude,
              longitude,
              name,
              id
            }
          },
          page_info
        }
         }"""

        data = {'q':q,
        'ref':'locations::show',
        'query_id':None}

        r = requests.post(url, data = data,headers=headers)
        try:
            d = json.loads(r.text)
        except ValueError as e:
            print r.text
            raise e
        time.sleep(1)
        if d["status"] == "fail":
            print "Sleeping a second"
            time.sleep(120)
        else:
            try:
                go = d["media"]["page_info"]["has_next_page"]
                images.extend(d["media"]["nodes"])
                output.write("\n".join(map(json.dumps,d["media"]["nodes"])) + "\n")
            except Exception:
                print json.dumps(d,indent=2)
            

if __name__ == "__main__":
    handle = sys.argv[1]
    save_loc = sys.argv[2]
    #getLocationData("152962574744049")
    print getAccountData(handle,save_loc)



    q_user = """ig_user(623582660) { media.after(AQCkz7k6kPDS-w_dYGNtFck9eH28BMeL0ehLVgH_bDp1d2LQbfLkXVNXVl4aVTmdpvLy-zIosZfBcvIRVd_IcEaRJu_dDwcWKhEqvXw8FEXAZBJU-CKD6GwAV2q88Z6vukU, 12) {
      count,
      nodes {
        __typename,
        caption,
        code,
        comments {
          count
        },
        comments_disabled,
        date,
        dimensions {
          height,
          width
        },
        display_src,
        id,
        is_video,
        likes {
          count
        },
        owner {
          id
        },
        thumbnail_src,
        video_views,
        location
      },
      page_info
    }
     }"""

    q_tags = """ig_hashtag(justin) { media.after(J0HWLSE9AAAAF0HWLSD6gAAAFigA, 1) {
      count,
      nodes {
        __typename,
        caption,
        code,
        comments {
          count
        },
        comments_disabled,
        date,
        dimensions {
          height,
          width
        },
        display_src,
        id,
        is_video,
        likes {
          count
        },
        link,
        url,
        owner {
          id
        },
        thumbnail_src,
        video_views,
        location {
          latitude,
          longitude,
          name,
          id
        }
      },
      page_info
    }
     }"""

    # Specific image info
    # https://www.instagram.com/p/BRAE135j9Ea/?taken-at=849479&__a=1&__b=1