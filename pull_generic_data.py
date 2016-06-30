#!/usr/bin/env/python

import common
import argparse
import time
import math
import numpy as np
from datetime import datetime

def main(args):
    number_users_per_user = int(math.ceil(float(args.num_users) * 2.0 / float(args.num_edges)))
    num_friends = int(float(args.balance) * number_users_per_user)
    num_followers = int(number_users_per_user - num_friends)

    user_list = [args.handle]
    all_tweets = common.get_timeline_in_range(args.handle, args.start_date, args.end_date, 3)

    new_users, new_tweets = common.get_active_users_around(args.handle, args.start_date, args.end_date, float(args.threshold), num_friends, num_followers, 3)
    user_list.extend(new_users)
    all_tweets.extend(new_tweets)
    get_more_from = np.random.choice(new_users, min(len(new_users), int(args.num_edges)), replace=False)

    for user in get_more_from:
        new_users, new_tweets = common.get_active_users_around(user, args.start_date, args.end_date, float(args.threshold), num_friends, num_followers, 3)
        user_list.extend(new_users)
        all_tweets.extend(new_tweets)

    processed_tweets = []

    for tweet in all_tweets:
        timestamp = str(datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y").strftime('%s'))
        handle = tweet['user']['screen_name']
        retweeted = tweet['retweeted_status']['user']['screen_name'] if 'retweeted_status' in tweet else tweet['in_reply_to_screen_name'] if 'in_reply_to_screen_name' in tweet else '-1'
        # format: timestamp, their username, username of who they're retweeting (-1 if not a retweet)
        processed_tweets.append((timestamp, handle, retweeted))

    a = common.UID_Assigner()
    for handle in user_list:
        a.get_UID(handle)

    all_tweets = []
    for tweet in processed_tweets:
        user = a.get_UID_no_add(tweet[1])
        retweeted = a.get_UID_no_add(tweet[2])
        all_tweets.append((tweet[0], user, retweeted))

    all_tweets = sorted(all_tweets, key = lambda (timestamp, uid, rid): timestamp)

    # write the usernames of the followers to our output file
    with open(args.output, 'wb') as output:
        for tweet in all_tweets:
            output.write(str(tweet[0]) + "," + str(tweet[1]) + "," + str(tweet[2]) + "\n")

# python pull_generic_data.py --handle <handle of starting node> --num_users <min number of users desired> --num_edges <number of users to branch out from around center> --balance <percentage of users followed> --threshold <activity level of "active user"> --output PATH/TO/processed_tweets/<handle>.txt --start_date YYYY-MM-DD --end_date YYYY-MM-DD
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Specify arguments')
    parser.add_argument('--handle', help='twitter handle of the first node to track from', required=True)
    parser.add_argument('--num_users', help='min number of users desired', required=True)
    parser.add_argument('--num_edges', help='number of users to branch out from around center', required=True)
    parser.add_argument('--balance', help='a float corresponding to the percentage of users who should be followed, not followers', required=True)
    parser.add_argument('--threshold', help='a float corresponding to the activity per day required to be "active"', required=True)
    parser.add_argument('--start_date', help='start date YYYY-mm-dd format', required=True)
    parser.add_argument('--end_date', help='ending date YYYY-mm-dd format', required=True)
    parser.add_argument('--output', help='the output file', required=True)
    
    args = parser.parse_args()
    
    start_time = time.time()
    main(args)
    end_time = time.time()
    print "Minutes elapsed:", (end_time-start_time)/60