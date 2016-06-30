#!/usr/bin/env/python

##############################################################
# Given a set of users and a timeframe, pulls all the tweets #
# of all the users and writes them unordered to a file.      #
##############################################################

import argparse
import time
import common
from datetime import datetime

def main(args):
    total_followers = common.file_len(args.users_file)
    a = common.UID_Assigner()
    with open(args.users_file, 'r') as users_file:
        with open(args.tweets_file, 'wb') as tweets_file:
            i = 1
            for handle in users_file:
                handle = handle.rstrip('\n')
                print "Processing user " + handle + "... (" + str(i) + "/" + str(total_followers) + ")"
                # get the tweets of a user
                tweets = common.get_timeline_in_range(handle, args.start_date, args.end_date, 3)
                # write down the tweets of a user
                for tweet in tweets:
                    timestamp = str(datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y").strftime('%s'))
                    retweeted = (tweet['retweeted_status']['user']['screen_name'] if 'retweeted_status' in tweet else (tweet['in_reply_to_screen_name'] if 'in_reply_to_screen_name' in tweet else ('-1')))
                    # format: timestamp, their username, username of who they're retweeting (-1 if not a retweet)
                    tweets_file.write(timestamp + "," + handle + "," + str(retweeted) + "\n")
                i += 1

# python get_tweets_generic.py --users_file PATH/TO/networks/<handle>.txt --tweets_file PATH/TO/tweets/<handle>.txt --start_date YYYY-MM-DD --end_date YYYY-MM-DD
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Specify arguments')
    parser.add_argument('--users_file', help='the however many users', required=True)
    parser.add_argument('--tweets_file', help='the output folder', required=True)
    parser.add_argument('--start_date', help='start date YYYY-mm-dd format', required=True)
    parser.add_argument('--end_date', help='ending date YYYY-mm-dd format', required=True)
    
    args = parser.parse_args()
    
    start_time = time.time()
    main(args)
    end_time = time.time()
    print "Minutes elapsed:", (end_time-start_time)/60