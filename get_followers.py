#!/usr/bin/env/python

#############################################################
# Given a broadcaster's twitter handle, gets a random list  #
# of <num_followers> followers of the broadcaster and saves #
# this into a file as directed by the user.                 #
#############################################################

import argparse
import sys
import time
import snowflake
import numpy as np

from common import *
from datetime import datetime
from tqdm import tqdm
from twython import Twython

from twython.exceptions import TwythonError
from twython.exceptions import TwythonAuthError
from twython.exceptions import TwythonRateLimitError


twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)

def get_timeline(screen_name):
    global twitter
    tweets = []

    # We need at least one tweet to start with
    while True:
        try:
            user_timeline = twitter.get_user_timeline(screen_name=screen_name, count=1)
            break
        except TwythonAuthError as e:
            print "TwythonAuthError..."
            time.sleep(1)
            continue
        except TwythonRateLimitError as e:
            print "TwythonRateLimitError... Waiting for 15 minutes"
            for timer in tqdm(range(15*60)):
                time.sleep(1)
            twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
            time.sleep(1)
            continue
    
    # put that one tweet into our list
    tweets.extend(user_timeline)
    tid = user_timeline[0]['id']
    
    # get more tweets! (up to 1500 more)
    print "Getting tweets of " + screen_name + "..."
    for i in tqdm(range(1,16)):
        while True:
            try:
                time.sleep(1)
                # this works because Twython gives us tweets in reverse chronological order (don't want to repeat, so set a max)
                user_timeline = twitter.get_user_timeline(screen_name=screen_name, count=100, max_id=tid, include_retweets=False)
                break
            except TwythonAuthError as e:
                print "TwythonAuthError..."
                continue
            except TwythonRateLimitError as e:
                print "TwythonRateLimitError... Waiting for 15 minutes"
                for timer in tqdm(range(15*60)):
                    time.sleep(1)
                twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
                continue

        tweets.extend(user_timeline)
        tid = user_timeline[-1]['id']
    
    return tweets


def get_timeline_in_range(screen_name, start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    result = []

    # pull the (up to) 1501 most recent tweets put out by user "<screen_name>"
    user_timeline = get_timeline(screen_name)

    # select out only those tweets which fall within the appropriate timeframe
    # (NOTE: this code assumes that the timeframe will be a subset of the 1401 most recent tweets,
    # which for recent events and/or typical usage, seems fairly reasonable)
    for tweet in user_timeline:
        dt = datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
        if dt >= start_date and dt <= end_date:
            result.append(tweet)

    # let our program's user know how many tweets fit in the time frame
    print "Found ", len(result), " tweets in date range ", start_date, " to ", end_date
    return result


def main(args):
    global twitter
    #Get tweets for the user in the date range
    user_timeline = get_timeline_in_range(args.handle, args.start_date, args.end_date)

    ################################################################################################################
    # 30 tweets to check is a magic number!!! Should it scale with the number of followers to pull?                #
    #                                                                                                              #
    # A rough calculation: users with followers in the millions can expect a minimum of 1000 retweets per tweet.   #
    # They're likely fine no matter what number of tweets you look at (unless you want, say >30K followers).       #
    #                                                                                                              #
    # Users with followers in the thousands can expect an average of ~30 retweets per tweet (with HIGH variance).  #
    # So, guessing for ~50% of retweets being duplicate users (likely a conservative estimate), seeking more       #
    # than ~450 followers means you probably want more tweets.                                                     #
    #                                                                                                              #
    # Users with less followers than 1000 probably need to scale the tweets such that the number of tweets scanned #
    # is larger than the number of followers you seek. (Or, at this point, just choose their followers directly,   #
    # not "active followers")                                                                                      #
    ################################################################################################################

    #select 30 tweets randomly in this range
    if len(user_timeline) > 30:
        user_timeline = np.random.choice(user_timeline, 30, replace=False)
    retweeter_ids = []

    #for each tweet, collect the retweeters
    print "Getting retweeters of " + args.handle + "..."
    for tweet in tqdm(user_timeline):
        while True:
            try:
                time.sleep(1)
                result = twitter.get_retweeters_ids(id=tweet['id'], count=50)
                retweeter_ids.extend(result['ids'])
                break
            except TwythonAuthError as e:
                print "TwythonAuthError..."
                continue
            except TwythonRateLimitError as e:
                print "TwythonRateLimitError... Waiting for 15 minutes"
                for timer in tqdm(range(15*60)):
                    time.sleep(1)
                twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
                continue

    #shuffle the retweeters to select retweeters (active followers) randomly
    np.random.shuffle(retweeter_ids)

    #select your followers
    num_follow_int = int(args.num_followers)
    print "selecting " + args.num_followers + " followers of " + args.handle + "..."
    followers = set()
    for id in retweeter_ids:
        followers.add(id)
        if len(followers) >= num_follow_int:
            break

    # change the type of all ids to string
    followers = map(lambda x: str(x), followers)
    
    # write the screen names of the followers to our output file
    with open(args.followers_file, 'wb') as output:
        print "Finding id of followers..."
        for i in tqdm(range((len(followers) - 1) / 100 + 1)):
            while True:
                try:
                    time.sleep(1)
                    # look up up to 100 users in one request (don't hit that rate limit!)
                    looking_up = ",".join(followers[i * 100 : min((i+1) * 100, len(followers))])
                    result = twitter.lookup_user(user_id=looking_up)
                    break
                except TwythonAuthError as e:
                    print "TwythonAuthError..."
                    continue
                except TwythonRateLimitError as e:
                    print "TwythonRateLimitError... Waiting for 15 minutes"
                    for timer in tqdm(range(15*60)):
                        time.sleep(1)
                    twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)
                    continue
            
            screen_names = map(lambda x: x['screen_name'], result)
            for name in screen_names:
                output.write(name+"\n")
    print "Done!"


# python get_followers.py --handle <handle> --follower_file PATH/TO/<handle>.txt --start_date YYYY-MM-DD --end_date YYYY-MM-DD
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Specify arguments')
    parser.add_argument('--handle', help='the twitter handle', required=True)
    parser.add_argument('--num_followers', help='number of followers desired', default=50)
    parser.add_argument('--followers_file', help='the output file', required=True)
    parser.add_argument('--start_date', help='start date', required=True)
    parser.add_argument('--end_date', help='end_date', required=True)
    args = parser.parse_args()
    main(args)