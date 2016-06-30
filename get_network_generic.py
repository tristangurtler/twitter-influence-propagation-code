#!/usr/bin/env/python

import argparse
import math
import numpy as np
import time
import common

def main(args):
    number_users_per_user = int(math.ceil(float(args.num_users) * 2.0 / float(args.num_edges)))
    num_friends = int(float(args.balance) * number_users_per_user)
    num_followers = int(number_users_per_user - num_friends)

    user_list = [args.handle]

    user_list.extend(common.get_active_users_around(args.handle, args.start_date, args.end_date, float(args.threshold), num_friends, num_followers, 3)[0])
    get_more_from = np.random.choice(user_list, min(len(user_list), int(args.num_edges)), replace=False)

    for user in get_more_from:
        user_list.extend(common.get_active_users_around(user, args.start_date, args.end_date, float(args.threshold), num_friends, num_followers, 3)[0])

    user_list = list(set(user_list))

    # write the usernames of the followers to our output file
    with open(args.users_file, 'wb') as output:
        for name in user_list:
            output.write(name+"\n")
    print "Done!"


# python get_network_general.py --handle <handle of starting node> --num_users <min number of users desired> --num_edges <number of users to branch out from around center> --balance <percentage of users followed> --threshold <activity level of "active user"> --users_file PATH/TO/followers/<handle>.txt --start_date YYYY-MM-DD --end_date YYYY-MM-DD
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Specify arguments')
    parser.add_argument('--handle', help='the central twitter handle', required=True)
    parser.add_argument('--num_users', help='min number of users desired', required=True)
    parser.add_argument('--num_edges', help='number of users to branch out from around center', required=True)
    parser.add_argument('--balance', help='a float corresponding to the percentage of users who should be followed, not followers', required=True)
    parser.add_argument('--threshold', help='a float corresponding to the activity per day required to be "active"', required=True)
    parser.add_argument('--users_file', help='the output file', required=True)
    parser.add_argument('--start_date', help='start date', required=True)
    parser.add_argument('--end_date', help='end_date', required=True)
    args = parser.parse_args()

    start_time = time.time()
    main(args)
    end_time = time.time()
    print "Minutes elapsed:", (end_time-start_time)/60