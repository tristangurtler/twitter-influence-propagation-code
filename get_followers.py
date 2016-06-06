#!/usr/bin/env/python

""" Given a twitter handles, this gets the list of followers of the user
    and saves the results in a file.
"""
import argparse
import sys
import time
import numpy as np

from common import *
from datetime import datetime
from twython import Twython

from twython.exceptions import TwythonError
from twython.exceptions import TwythonAuthError
from twython.exceptions import TwythonRateLimitError


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
    try:
      #tweets are returned in reverse chronological order
      user_timeline = twitter.get_user_timeline(screen_name=screen_name,
                                                count=100, max_id=tweet_ids[-1], include_retweets=False)
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
  return tweets.values()


def get_timeline_in_range(screen_name, start_date, end_date):
  user_timeline = get_timeline(screen_name)
  start_date = datetime.strptime(start_date, "%Y-%m-%d")
  end_date = datetime.strptime(end_date, "%Y-%m-%d")
  result = []
  for tweet in user_timeline:
    dt = datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
    if dt >= start_date and dt <= end_date:
      result.append(tweet)
  print "Found ", len(result), " tweets in date range ", start_date, " to ", end_date
  return result


def main(args):
  global twitter
  #Get tweets for the user in the date range
  user_timeline = get_timeline_in_range(args.handle, args.start_date, args.end_date)

  #select 30 tweets randomly in this range
  if len(user_timeline) > 30:
    user_timeline = np.random.choice(user_timeline, 30, replace=False)
  retweeter_ids = []

  #for each tweet, collect the retweeters
  for tweet in user_timeline:
    time.sleep(3)
    try:
      result = twitter.get_retweeters_ids(id=tweet['id'], count=50)
      retweeter_ids.extend(result['ids'])
      print "...."
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

  #shuffle the retweeters to select random 50 retweeters as active followers
  np.random.shuffle(retweeter_ids)

  print "selecting 50 followers ..."
  #select 50 followers
  followers = set()
  for id in retweeter_ids:
    followers.add(id)
    if len(followers) >= 50:
      break

  followers = map(lambda x: str(x), followers)
  with open(args.follower_file, 'wb') as output:
    for id in followers:
      time.sleep(2)
      try:
        result = twitter.lookup_user(user_id=id)
      except TwythonAuthError as e:
        print "TwythonAuthError..."
        continue
      except TwythonError as e:
        print "TwythonError..."
      except TwythonRateLimitError as e:
        print "TwythonRateLimitError... Waiting for 240 seconds"
        time.sleep(240)
        twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
        continue
      screen_name = result[0]['screen_name']
      output.write(screen_name+"\n")


#python get_followers.py --handle FLOTUS --follower_file /home/dapurv5/Desktop/influence_propagation/followers/FLOTUS.txt --start_date 2016-01-15 --end_date 2016-01-21
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Specify arguments')
  parser.add_argument('--handle', help='the twitter handle', required=True)
  parser.add_argument('--follower_file', help='the output file', required=True)
  parser.add_argument('--start_date', help='start date', required=True)
  parser.add_argument('--end_date', help='end_date', required=True)
  args = parser.parse_args()
  main(args)