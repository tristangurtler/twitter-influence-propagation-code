#!/usr/bin/env/python

##############################################################
# Given a broadcaster's twitter handle, a list of followers, #
# and a timeframe, pulls all the tweets of the broadcaster   #
# and followers and writes them unordered to a file.         #
##############################################################

import argparse
import time
import common
from datetime import datetime

def main(args):
    total_followers = common.file_len(args.followers_file)
    with open(args.followers_file, 'r') as followers_file:
        with open(args.tweets_file, 'wb') as tweets_file:
            # get the tweets of the broadcaster
            tweets = common.get_timeline_in_range(args.handle, args.start_date, args.end_date, 3)
            # write the tweets of the broadcaster
            print "Processing broadcaster " + args.handle
            for tweet in tweets:
                timestamp = str(datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y").strftime('%s'))
                # format: timestamp, their username, username of who they're retweeting (-1 if not a retweet)
                tweets_file.write(timestamp + "," + args.handle + "," + str(-1) + "\n")

            i = 1
            for handle in followers_file:
                handle = handle.rstrip('\n')
                print "Processing follower " + handle + "... (" + str(i) + "/" + str(total_followers) + ")"
                # get the tweets of their followers
                tweets = common.get_timeline_in_range(handle, args.start_date, args.end_date, 3)
                # write the tweets of their followers
                for tweet in tweets:
                    timestamp = str(datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y").strftime('%s'))
                    # format: timestamp, their username, username of who they're retweeting (-1 if not a retweet)
                    tweets_file.write(timestamp + "," + handle + "," + (args.handle if args.handle in tweet['text'] else str(-1)) + "\n")
                i += 1

# python get_tweets.py --handle <handle> --followers_file PATH/TO/followers/<handle>.txt --tweets_file PATH/TO/tweets/<handle>.txt --start_date YYYY-MM-DD --end_date YYYY-MM-DD
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
    print "Minutes elapsed:", (end_time-start_time)/60