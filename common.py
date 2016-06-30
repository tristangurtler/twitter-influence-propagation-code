#!/usr/bin/env/python

import snowflake
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
APP_KEY = <App Key ("Consumer Key") goes here>
ACCESS_TOKEN = <Access token (see below) goes here>
#################################################################
# In order to get an access token, use the following code       #
#                                                               #
# APP_SECRET = <App Secret ("Consumer Secret") goes here>       #
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
# gets a user's recent timeline from twitter, up to the amount of tweets you specify)
# @arg screen_name -- the username of the user we want to pull tweets for
# @arg num_tweets -- the (minimum) number of tweets you want from the user (only applies if they have tweeted at least that many)
# @arg waiting -- how many seconds to wait in between requests (very important to not hit rate limiting)
# @return their recent timeline
def get_timeline(screen_name, num_tweets, waiting):
    twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
    tweets = []
    num_iter = int(num_tweets / 200) + 1
    num_iter = num_iter if num_iter <= 16 else 16
    num_iter = num_iter if num_iter >= 1 else 1

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
    
    # get more tweets!
    print "Getting tweets of " + screen_name + "..."
    for i in tqdm(range(num_iter)):
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
# THIS CODE ASSUMES that the time range falls within their 3200 most recent tweets (beyond that, Twitter won't give them to us anyways)
# @arg screen_name -- the username of the user we want to pull tweets for
# @arg start_date -- a string referring to the first day we want to pull tweets for
# @arg end_date -- a string referring to the last day we want to pull tweets for
# @arg waiting -- how many seconds to wait in between requests (very important to not hit rate limiting)
# @return their recent timeline from start_date to end_date
def get_timeline_in_range(screen_name, start_date, end_date, waiting):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    
    # we use the code provided by Nick Galbreath (see snowflake.py) to derive a Twitter id from our timestamps to use as max and min values
    start_id = snowflake.utc2snowflake(time.mktime(start_date.timetuple()))
    end_id = snowflake.utc2snowflake(time.mktime(end_date.timetuple()))

    twitter = Twython(common.APP_KEY, access_token=common.ACCESS_TOKEN)
    tweets = []

    # We need at least one tweet to start with (choose it to be in the timeframe)
    while True:
        try:
            user_timeline = twitter.get_user_timeline(screen_name=screen_name, count=1, since_id=start_id, max_id=end_id)
            break
        except TwythonAuthError as e:
            print "TwythonAuthError..."
            time.sleep(waiting)
            return tweets
        except TwythonRateLimitError as e:
            print "TwythonRateLimitError... Waiting for 3 minutes (may take multiple waits)"
            for timer in tqdm(range(3*60)):
                time.sleep(1)
            twitter = Twython(common.APP_KEY, access_token=common.ACCESS_TOKEN)
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
    
    # get every tweet in the timeframe that we can, and nothing outside of it
    print "Getting tweets of " + screen_name + "..."
    while True:
        while True:
            try:
                time.sleep(waiting)
                # this works because Twython gives us tweets in reverse chronological order (don't want to repeat, so set a max, don't want to go too far, so set a min)
                user_timeline = twitter.get_user_timeline(screen_name=screen_name, count=200, max_id=tid, since_id=start_id)
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
    
    print "Found " + str(len(tweets)) + " tweets in date range " + str(start_date) + " to " + str(end_date)
    return tweets

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

    # get friends and followers around a central user
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

    # choose out random friends and followers from the previous list, with a safety factor of 2 times as many as asked for to account for the fact that some users will not be active
    following = map(lambda x: str(x), np.random.choice(following['ids'], min(int(num_friends * 2), len(following['ids'])), replace=False))
    followers = map(lambda x: str(x), np.random.choice(followers['ids'], min(int(num_followers * 2), len(followers['ids'])), replace=False))
    following = get_usernames(following, waiting)
    followers = get_usernames(followers, waiting)

    # figure out how many tweets are necessary to deem a user "active"
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    threshold = abs(end-start).days * threshold

    # collect out as many active followed users from the central user (and their tweets) as we can, up to a limit of the number asked for
    collected_friends = []
    for user in following:
        user_timeline = get_timeline_in_range(user, start_date, end_date, waiting)
        if len(user_timeline) >= threshold:
            collected_friends.append(user)
            all_tweets.extend(user_timeline)
        if len(collected_friends) >= num_friends:
            break

    # collect out as many active followers from the central user (and their tweets) as we can, up to a limit of the number asked for
    collected_followers = []
    for user in followers:
        user_timeline = get_timeline_in_range(user, start_date, end_date, waiting)
        if len(user_timeline) >= threshold:
            collected_followers.append(user)
            all_tweets.extend(user_timeline)
        if len(collected_followers) >= num_followers:
            break

    # return our list of users and their tweets from the time period in question
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
    # (use this to filter out external users)
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