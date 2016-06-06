#!/usr/bin/env/python

import argparse
import time
import sys

from common import *
from datetime import datetime
from twython import Twython

from twython.exceptions import TwythonError
from twython.exceptions import TwythonAuthError
from twython.exceptions import TwythonRateLimitError
"""
AndrewYNg
BillGates
FLOTUS 20160114 20160122  #Michelle Obama's birthday on January 18th
"""

twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)

def get_timeline(screen_name):
  global twitter
  tweets = {}
  tweet_ids = []

  while True:
    try:
      time.sleep(2)
      user_timeline = twitter.get_user_timeline(screen_name=screen_name, count=1)
      break
    except TwythonAuthError as e:
      print "TwythonAuthError..."
      continue
    except TwythonRateLimitError as e:
      print "TwythonRateLimitError... Waiting for 240 seconds"
      time.sleep(240)
      twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
      continue
    except TwythonError as e:
      print "TwythonError..."

  for tweet in user_timeline:
    tid = tweet['id']
    tweets[tid] = tweet
    tweet_ids.append(tid)

  for i in range(1,15):
    time.sleep(2)
    print "..."
    try:
      #tweets are returned in reverse chronological order
      user_timeline = twitter.get_user_timeline(screen_name=screen_name,
                                                count=100, max_id=tweet_ids[-1])
    except TwythonAuthError as e:
      print "TwythonAuthError..."
      continue
    except TwythonRateLimitError as e:
      print "TwythonRateLimitError... Waiting for 240 seconds"
      time.sleep(240)
      twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
      continue
    except TwythonError as e:
      print "TwythonError..."

    for tweet in user_timeline:
      tid = tweet['id']
      tweets[tid] = tweet
      tweet_ids.append(tid)
  print "returning ", len(tweets.values()), " tweets .."
  return tweets.values()


def main(args):
  global twitter
  start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
  end_date = datetime.strptime(args.end_date, "%Y-%m-%d")

  with open(args.followers_file, 'r') as followers_file:
    with open(args.tweets_file, 'wb') as tweets_file:
      #write the tweets of the celebrity node
      handle = args.handle
      tweets = get_timeline(handle)
      for tweet in tweets:
        dt = datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
        if dt >= start_date and dt <= end_date:
          timestamp = str(dt.strftime('%s'))
          tweets_file.write(timestamp + "," + str(args.handle) + "," + str(-1) + "\n")

      #write the tweets for its followers
      for handle in followers_file:
        handle = handle.rstrip('\n')
        print "processing handle ", handle
        tweets = get_timeline(handle)
        for tweet in tweets:
          dt = datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
          if dt >= start_date and dt <= end_date:
            is_retweet_of_parent = args.handle in tweet['text']
            timestamp = str(dt.strftime('%s'))
            if is_retweet_of_parent:
              tweets_file.write(timestamp + "," + handle + "," + args.handle + "\n")
            else:
              tweets_file.write(timestamp + "," + handle + "," + str(-1) + "\n")


#python get_tweets.py --handle FLOTUS --followers_file /home/dapurv5/Desktop/influence_propagation/followers/FLOTUS.txt --tweets_file /home/dapurv5/Desktop/influence_propagation/tweets/FLOTUS.txt --start_date 2016-01-01 --end_date 2016-01-30
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Specify arguments')
  parser.add_argument('--handle', help='twitter handle of this celebrity', required=True)
  parser.add_argument('--followers_file', help='the top 50 followers', required=True)
  parser.add_argument('--tweets_file', help='the output folder', required=True)
  parser.add_argument('--start_date', help='start date YYYY-mm-dd format', required=True)
  parser.add_argument('--end_date', help='ending date YYYY-mm-dd format', required=True)

  args = parser.parse_args()

  start_time = time.time()
  main(args)
  end_time = time.time()
  print "Minutes elapsed", (end_time-start_time)/60