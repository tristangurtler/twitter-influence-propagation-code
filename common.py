#!/usr/bin/env/python

import time
import numpy as np
from datetime import datetime
from tqdm import tqdm
from twython import Twython
from twython.exceptions import TwythonError
from twython.exceptions import TwythonAuthError
from twython.exceptions import TwythonRateLimitError

# Twitter authentication credentials
# use like so: twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
APP_KEY = <App Key goes here>
ACCESS_TOKEN = <Access Token goes here>
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


# get_timeline(screen_name, waiting)
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
            return tweets
        except TwythonRateLimitError as e:
            print "TwythonRateLimitError... Waiting for 3 minutes (may take multiple waits)"
            for timer in tqdm(range(3*60)):
                time.sleep(1)
            twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
            time.sleep(waiting)
            continue
        except TwythonError as e:
            print "TwythonError: " + str(e.error_code) + "..."
            continue
    
    # put that one tweet into our list
    tweets.extend(user_timeline)
    if not user_timeline:
        time.sleep(waiting)
        return tweets
    tid = user_timeline[0]['id']
    
    # get more tweets! (up to 1600 more)
    print "Getting tweets of " + screen_name + "..."
    for i in tqdm(range(8)):
        while True:
            try:
                time.sleep(waiting)
                # this works because Twython gives us tweets in reverse chronological order (don't want to repeat, so set a max)
                user_timeline = twitter.get_user_timeline(screen_name=screen_name, count=200, max_id=tid)
                break
            except TwythonAuthError as e:
                print "TwythonAuthError..."
                return tweets
            except TwythonRateLimitError as e:
                print "TwythonRateLimitError... Waiting for 3 minutes (may take multiple waits)"
                for timer in tqdm(range(3*60)):
                    time.sleep(1)
                twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
                continue
            except TwythonError as e:
                print "TwythonError: " + str(e.error_code) + "..."
                continue

        # if twitter gave us no tweets, there's no more to get
        if not user_timeline:
            break

        # otherwise save them and keep track of which one's the oldest (and set one below it to be the max we'll allow)
        tweets.extend(user_timeline)
        tid = user_timeline[-1]['id'] - 1
    
    print "Found " + str(len(tweets)) + " tweets total"
    return tweets

# get_timeline_in_range(screen_name, start_date, end_date, waiting)
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

    # pull the (up to) 1601 most recent tweets put out by user "<screen_name>"
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

# get_retweeters(user_timeline, waiting)
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
            except TwythonError as e:
                print "TwythonError: " + str(e.error_code) + "..."
                continue

    return list(set(retweeter_ids))

# get_active_users_around(center, start_date, end_date, threshold, num_friends, num_followers, waiting)
# gets a group of people in the network around the center user
# @arg center -- the central user of the network we intend to build
# @arg start_date -- a string referring to the first day we want to pull tweets for
# @arg end_date -- a string referring to the last day we want to pull tweets for
# @arg threshold -- how many tweets per day a user needs to be "active"
# @arg num_friends -- maximum number of friends to return
# @arg num_followers -- maximum number of followers to return
# @arg waiting -- how many seconds to wait in between requests (very important to not hit rate limiting)
# @return people who retweeted some tweet within user_timeline, by numerical id
def get_active_users_around(center, start_date, end_date, threshold, num_friends, num_followers, waiting):
    twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
    user_ids = []
    all_tweets = []

    print "Getting users..."
    while True:
        try:
            following = twitter.get_friends_ids(screen_name=center, count=5000)
            time.sleep(0.1)
            followers = twitter.get_followers_ids(screen_name=center, count=5000)
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
        except TwythonError as e:
            print "TwythonError: " + str(e.error_code) + "..."
            time.sleep(waiting)
            continue

    following = map(lambda x: str(x), np.random.choice(following['ids'], min(int(num_friends * 2), len(following['ids'])), replace=False))
    followers = map(lambda x: str(x), np.random.choice(followers['ids'], min(int(num_followers * 2), len(followers['ids'])), replace=False))
    following = get_usernames(following, waiting)
    followers = get_usernames(followers, waiting)

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    threshold = abs(end-start).days * threshold

    collected_friends = []
    for user in following:
        user_timeline = get_timeline_in_range(user, start_date, end_date, waiting)
        if len(user_timeline) >= threshold:
            collected_friends.append(user)
            all_tweets.extend(user_timeline)
        if len(collected_friends) >= num_friends:
            break

    collected_followers = []
    for user in followers:
        user_timeline = get_timeline_in_range(user, start_date, end_date, waiting)
        if len(user_timeline) >= threshold:
            collected_followers.append(user)
            all_tweets.extend(user_timeline)
        if len(collected_followers) >= num_followers:
            break

    user_ids.extend(collected_friends)
    user_ids.extend(collected_followers)
    return (user_ids, all_tweets)

# get_usernames(users, waiting)
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
            except TwythonError as e:
                print "TwythonError: " + str(e.error_code) + "..."
                continue

        screen_names.extend(map(lambda x: x['screen_name'], result))

    return screen_names


# UID_Assigner
# a class to facilitate ease in stripping usernames down to arbitrary node IDs,
# as used for postprocessing
class UID_Assigner:
    # UIDAssigner(leader)
    # initializes the class to know who the broadcaster (node 1) is
    # @arg leader -- username of the broadcaster to track
    def __init__(self, leader):
        self.curr_uid = 2
        self.d = {"-1" : 0, leader : 1}

    # UIDAssigner()
    # initializes the class without reference to a broadcaster
    def __init__(self):
        self.curr_uid = 1
        self.d = {"-1" : 0}

    # a.get_UID(handle)
    # gets (or assigns, if necessary) the proper node ID of a user
    # @arg handle -- username to find a node ID for
    # @return the appropriate node ID for handle
    def get_UID(self, handle):
        if handle in self.d:
            return self.d[handle]
        self.d[handle] = self.curr_uid
        self.curr_uid += 1
        return self.curr_uid - 1

    # a.get_UID_no_add(handle)
    # gets the proper node ID of a user, only returning a valid value if they already exist
    # @arg handle -- username to find a node ID for
    # @return the appropriate node ID for handle
    def get_UID_no_add(self, handle):
        if handle in self.d:
            return self.d[handle]
        return 0

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