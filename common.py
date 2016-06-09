#!/usr/bin/env/python

import time
from datetime import datetime
from tqdm import tqdm
from twython import Twython
from twython.exceptions import TwythonAuthError
from twython.exceptions import TwythonRateLimitError

# Twitter authentication credentials
# use like so: twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
APP_KEY = 'K96DwyMgH0tVmNFUAGTmO7HsQ'
ACCESS_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAIg8vgAAAAAAwE1eH154vEZ5vp5H%2BqdwMbyoRwA%3DMytkn7H2pW16syzzXmmoPd7uOg6GAcUhJAFjeNLebI3PXQyyaZ'
#################################################################
# In order to get an access token, use the following code       #
#                                                               #
# APP_SECRET = '<App Secret ("Consumer Secret") goes here>'     #
#                                                               #
# twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)       #
# ACCESS_TOKEN = twitter.obtain_access_token()                  #
#                                                               #
# with open("token.txt", 'wb') as output:                       #
#     output.write(ACCESS_TOKEN + "\n")                         #
#                                                               #
# You will find the access token written in a file "token.txt"  #
# in the folder you run this code in                            #
#################################################################


# get_timeline(screen_name)
# gets a user's recent timeline from twitter, up to the 1501 most recent tweets (if there are that many)
# @arg screen_name -- the username of the user we want to pull tweets for
# @arg waiting -- how many seconds to wait in between requests (very important to not hit rate limiting)
# @return their recent timeline
def get_timeline(screen_name, waiting):
    twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
    tweets = []

    # We need at least one tweet to start with
    while True:
        try:
            user_timeline = twitter.get_user_timeline(screen_name=screen_name, count=1)
            break
        except TwythonAuthError as e:
            print "TwythonAuthError..."
            time.sleep(waiting)
            continue
        except TwythonRateLimitError as e:
            print "TwythonRateLimitError... Waiting for 3 minutes (may take multiple waits)"
            for timer in tqdm(range(3*60)):
                time.sleep(1)
            twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
            time.sleep(waiting)
            continue
    
    # put that one tweet into our list
    tweets.extend(user_timeline)
    tid = user_timeline[0]['id']
    
    # get more tweets! (up to 1500 more)
    print "Getting tweets of " + screen_name + "..."
    for i in tqdm(range(1,16)):
        while True:
            try:
                time.sleep(waiting)
                # this works because Twython gives us tweets in reverse chronological order (don't want to repeat, so set a max)
                user_timeline = twitter.get_user_timeline(screen_name=screen_name, count=100, max_id=tid, include_retweets=False)
                break
            except TwythonAuthError as e:
                print "TwythonAuthError..."
                continue
            except TwythonRateLimitError as e:
                print "TwythonRateLimitError... Waiting for 3 minutes (may take multiple waits)"
                for timer in tqdm(range(3*60)):
                    time.sleep(1)
                twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
                continue

        # if twitter gave us no tweets, there's no more to get
        if not user_timeline:
            break

        # otherwise save them and keep track of which one's the oldest (and set one below it to be the max we'll allow)
        tweets.extend(user_timeline)
        tid = user_timeline[-1]['id'] - 1
    
    print "Found " + str(len(tweets)) + " tweets total"
    return tweets

# get_timeline_in_range(screen_name, start_date, end_date)
# gets a user's timeline within a specific time range from twitter
# THIS CODE ASSUMES that the time range falls within their 1501 most recent tweets
# @arg screen_name -- the username of the user we want to pull tweets for
# @arg start_date -- a string referring to the first day we want to pull tweets for
# @arg end_date -- a string referring to the last day we want to pull tweets for
# @arg waiting -- how many seconds to wait in between requests (very important to not hit rate limiting)
# @return their recent timeline from start_date to end_date
def get_timeline_in_range(screen_name, start_date, end_date, waiting):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    result = []

    # pull the (up to) 1501 most recent tweets put out by user "<screen_name>"
    user_timeline = get_timeline(screen_name, waiting)

    # select out only those tweets which fall within the appropriate timeframe
    # (NOTE: this code assumes that the timeframe will be a subset of the 1401 most recent tweets,
    # which for recent events and/or typical usage, seems fairly reasonable)
    for tweet in user_timeline:
        dt = datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
        if dt >= start_date and dt <= end_date:
            result.append(tweet)

    # let our program's user know how many tweets fit in the time frame
    print "Found " + str(len(result)) + " tweets in date range " + str(start_date) + " to " + str(end_date)
    return result

# get_retweeters(user_timeline)
# gets every person to retweet any of a set of tweets (or, up to 100 per tweet, anyways)
# @arg user_timeline -- the set of tweets to find retweeters for
# @arg waiting -- how many seconds to wait in between requests (very important to not hit rate limiting)
# @return people who retweeted some tweet within user_timeline, by numerical id
def get_retweeters(user_timeline, waiting):
    twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
    retweeter_ids = []

    #for each tweet, collect the retweeters
    print "Getting retweeters..."
    for tweet in tqdm(user_timeline):
        while True:
            try:
                time.sleep(waiting)
                result = twitter.get_retweeters_ids(id=tweet['id'], count=100)
                retweeter_ids.extend(result['ids'])
                break
            except TwythonAuthError as e:
                print "TwythonAuthError..."
                continue
            except TwythonRateLimitError as e:
                print "TwythonRateLimitError... Waiting for 3 minutes (may take multiple waits)"
                for timer in tqdm(range(3*60)):
                    time.sleep(1)
                twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
                continue

    return list(set(retweeter_ids))

# get_usernames(users)
# gets the username for every numerical id (in string form) in users
# @arg users -- a set of stringified numerical ids for our users
# @arg waiting -- how many seconds to wait in between requests (very important to not hit rate limiting)
# @return usernames for these users
def get_usernames(users, waiting):
    twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
    screen_names = []

    print "Finding screen names of users..."
    for i in tqdm(range((len(users) - 1) / 100 + 1)):
        while True:
            try:
                time.sleep(waiting)
                # look up up to 100 users in one request (don't hit that rate limit!)
                looking_up = ",".join(users[i * 100 : min((i+1) * 100, len(users))])
                result = twitter.lookup_user(user_id=looking_up)
                break
            except TwythonAuthError as e:
                print "TwythonAuthError..."
                continue
            except TwythonRateLimitError as e:
                print "TwythonRateLimitError... Waiting for 3 minutes (may take multiple waits)"
                for timer in tqdm(range(15*60)):
                    time.sleep(1)
                twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
                continue

        screen_names.extend(map(lambda x: x['screen_name'], result))

    return screen_names

# file_len(fname)
# gets the number of lines in a file
# @arg fname -- name of the file to check
# @return number of lines in fname
def file_len(fname):
    i = -1
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

class UID_Assigner:
    def __init__(self, leader):
        self.leader = leader
        self.curr_uid = 2
        self.d = {"-1" : 0, leader : 1}

    def get_UID(self, handle):
        if handle in self.d:
            return self.d[handle]
        self.d[handle] = self.curr_uid
        self.curr_uid += 1
        return self.curr_uid - 1