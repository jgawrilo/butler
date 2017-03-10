#!/usr/bin/env python
# encoding: utf-8

import tweepy
import csv
import os
import sys
import time

# The consumer key and secret will be generated for you after
consumer_key="BC28vJwCUtsccCLckbQHqchYF"
consumer_secret="GBAIf2XXmcgqUK0InYfvDFfcaN6Csr81tQqHPDA9YbvtWAa8NB"

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
access_key="762648385-HFfCUfrsrAgjzjwRl2qceUiqQQzeaHPvR4zGfX4d"
access_secret="At0YFxAoDIHVfbslri3zdZqHDMhP7OWiak8UZn9k5n6rC"


def get_all_tweets(screen_name,save_loc):
    try:
        #Twitter only allows access to a users most recent 3240 tweets with this method
        
        #authorize twitter, initialize tweepy
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_key, access_secret)
        api = tweepy.API(auth)
        
        #initialize a list to hold all the tweepy Tweets
        alltweets = []  
        
        #make initial request for most recent tweets (200 is the maximum allowed count)
        new_tweets = api.user_timeline(screen_name = screen_name,count=200)
        
        #save most recent tweets
        alltweets.extend(new_tweets)

        if alltweets:
        
            #save the id of the oldest tweet less one
            oldest = alltweets[-1].id - 1

            last_date = alltweets[-1].created_at
            
            #keep grabbing tweets until there are no tweets left to grab
            while len(new_tweets) > 0 and str(last_date):
                print "getting tweets before %s, %s" % (oldest, last_date)
                
                #all subsiquent requests use the max_id param to prevent duplicates
                new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest)
                
                #save most recent tweets
                alltweets.extend(new_tweets)
                
                #update the id of the oldest tweet less one
                oldest = alltweets[-1].id - 1
                last_date = alltweets[-1].created_at
                
                print "...%s tweets downloaded so far" % (len(alltweets))
            
            #transform the tweepy tweets into a 2D array that will populate the csv 
            outtweets = [[tweet.id_str, tweet.created_at, tweet.text.replace("\n", "\\n").encode("utf-8"), tweet.entities.get('hashtags')] for tweet in alltweets]
            
            #write the csv  
            with open(save_loc + '%s_twitter.csv' % screen_name, 'wb') as f:
                writer = csv.writer(f,delimiter="\t")
                writer.writerow(["id","created_at","text","hashtags"])
                writer.writerows(outtweets)
            
            pass
    except tweepy.error.RateLimitError as e:
        print "Hit rate limit..."
        time.sleep(60*15)
    #except tweepy.error.TweepError as e:
    #    print "Error...moving on:"



if __name__ == '__main__':

    handle = sys.argv[1]
    save_loc = sys.argv[2]
    print handle
    get_all_tweets(handle,save_loc)





