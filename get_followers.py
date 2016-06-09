#!/usr/bin/env/python

#############################################################
# Given a broadcaster's twitter handle, gets a random list  #
# of <num_followers> followers of the broadcaster and saves #
# this into a file as directed by the user.                 #
#############################################################

import argparse
import numpy as np
import common

def main(args):
    #Get tweets for the user in the date range
    user_timeline = common.get_timeline_in_range(args.handle, args.start_date, args.end_date, 1)

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
    
    # get active followers (defined as having retweeted the broadcaster ever)
    retweeter_ids = common.get_retweeters(user_timeline, 1)

    # select your followers randomly and change the id numbers to strings for processing
    followers = map(lambda x: str(x), np.random.choice(retweeter_ids, min(int(args.num_followers), len(retweeter_ids)), replace=False))
    
    # turn the id numbers (as strings) into usernames
    screen_names = common.get_usernames(followers, 1)

    # write the usernames of the followers to our output file
    with open(args.followers_file, 'wb') as output:
        for name in screen_names:
            output.write(name+"\n")
    print "Done!"


# python get_followers.py --handle <handle> --num_followers <how many followers you desire> --followers_file PATH/TO/followers/<handle>.txt --start_date YYYY-MM-DD --end_date YYYY-MM-DD
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Specify arguments')
    parser.add_argument('--handle', help='the twitter handle', required=True)
    parser.add_argument('--num_followers', help='number of followers desired', default=50)
    parser.add_argument('--followers_file', help='the output file', required=True)
    parser.add_argument('--start_date', help='start date', required=True)
    parser.add_argument('--end_date', help='end_date', required=True)
    args = parser.parse_args()
    main(args)