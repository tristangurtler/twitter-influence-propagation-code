import common
import argparse
import time
import numpy as np
from datetime import datetime

def main(args):
    #Get tweets for the user in the date range
    leader_timeline = common.get_timeline_in_range(args.handle, args.start_date, args.end_date, 3)

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
    if len(leader_timeline) > 30:
        leader_timeline = np.random.choice(leader_timeline, 30, replace=False)
    
    # get active followers (defined as having retweeted the broadcaster ever)
    retweeter_ids = common.get_retweeters(leader_timeline, 1)

    # select your followers randomly and change the id numbers to strings for processing
    followers = map(lambda x: str(x), np.random.choice(retweeter_ids, min(int(args.num_followers), len(retweeter_ids)), replace=False))
    
    # turn the id numbers (as strings) into usernames
    screen_names = common.get_usernames(followers, 1)

    all_tweets = []
    # process the tweets of the broadcaster
    print "Processing broadcaster " + args.handle
    for tweet in leader_timeline:
        timestamp = str(datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y").strftime('%s'))
        all_tweets.append((long(timestamp), 1, 0))

    # do stuff with the followers
    for (handle, i) in zip(screen_names, range(1, len(screen_names) + 1)):
        print "Processing follower " + handle + "... (" + str(i) + "/" + str(len(screen_names)) + ")"
        # get the followers' tweets
        follower_tweets = common.get_timeline_in_range(handle, args.start_date, args.end_date, 3)
        # process the followers' tweets
        for tweet in follower_tweets:
            timestamp = str(datetime.strptime(tweet['created_at'], "%a %b %d %H:%M:%S +0000 %Y").strftime('%s'))
            # QUESTION: is this really the best way to tell if a tweet is a RT? it is, at least, one way you'd do directed tweets/replies, just...
            all_tweets.append((long(timestamp), i + 1, (1 if args.handle in tweet['text'] else 0)))

    # sort all tweets by timestamp, then write them to file
    all_tweets = sorted(all_tweets, key = lambda (timestamp, fid, cid): timestamp)
    with open(args.output, 'wb') as output:
        for tweet in all_tweets:
            output.write(str(tweet[0]) + "," + str(tweet[1]) + "," + str(tweet[2]) + "\n")

# python pull_star_data.py --handle <handle of broadcaster> --num_followers <how many followers you desire> --start_date YYYY-MM-DD --end_date YYYY-MM-DD --output PATH/TO/OUTPUT/<handle>.txt
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Specify arguments')
    parser.add_argument('--handle', help='twitter handle of this celebrity', required=True)
    parser.add_argument('--num_followers', help='number of followers desired', default=50)
    parser.add_argument('--start_date', help='start date YYYY-mm-dd format', required=True)
    parser.add_argument('--end_date', help='ending date YYYY-mm-dd format', required=True)
    parser.add_argument('--output', help='the output file', required=True)
    
    args = parser.parse_args()
    
    start_time = time.time()
    main(args)
    end_time = time.time()
    print "Minutes elapsed:", (end_time-start_time)/60