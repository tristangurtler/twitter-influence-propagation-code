#!/usr/bin/env/python

#######################################################
# Takes the file generated by get_tweets_generic.py,  #
# assigns each twitter handle a numeric value, and    #
# sorts all tweet events by their time                #
#######################################################

import argparse
import common

def main(args):
    a = common.UID_Assigner()
    # begin by noting down only the usernames that are used in our data (so that external retweets are properly ignored)
    with open(args.users_file, 'r') as users_file:
        for handle in users_file:
            handle = handle.rstrip('\n')
            a.get_UID(handle)

    tweet_events = []

    with open(args.tweets_file, 'r') as tweets_file:
        for line in tweets_file:
            line = line.strip('\n')
            line = line.split(",") 

            # reduce usernames to node numbers, ignoring external retweets (1-indexed, and 0 indicates NULL)
            user = a.get_UID_no_add(line[1])
            retweeted = a.get_UID_no_add(line[2])

            # keep track of the triple: (timestamp, user's id, id of who they retweeted)
            if user != 0:
                tweet_events.append((long(line[0]), str(user), str(retweeted)))

    # sort the events by timestamp
    tweet_events = sorted(tweet_events, key = lambda (timestamp, uid, rid): timestamp)

    with open(args.processed_file, 'wb') as output:
        # write down the triples in order
        for tweet in tweet_events:
            output.write(str(tweet[0]) + "," + tweet[1] + "," + tweet[2]+"\n")

# python postprocessing_generic.py --users_file PATH/TO/networks/<handle>.txt --tweets_file PATH/TO/tweets/<handle>.txt --processed_file PATH/TO/tweets_processed/<handle>.txt
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Specify arguments')
    parser.add_argument('--users_file', help='the however many users', required=True)
    parser.add_argument('--tweets_file', help='the tweets file produced by get_tweets_generic.py', required=True)
    parser.add_argument('--processed_file', help='the output file', required=True)

    args = parser.parse_args()
    main(args)