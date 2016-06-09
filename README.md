# twitter-influence-propagation-code

Code to generate datasets as used in the twitter [influence propagation work](http://arxiv.org/pdf/1603.08981v1.pdf) performed by Li et al.

```
@article{Li_DetectingWeakChanges,
    author    = {Shuang Li and Yao Xie and Mehrdad Farajtabar and Le Song},
    title     = {Detecting weak changes in dynamic events over networks},
    journal   = {CoRR},
    volume    = {abs/1603.08981},
    year      = {2016},
    url       = {http://arxiv.org/abs/1603.08981},
    timestamp = {Sat, 02 Apr 2016 11:49:48 +0200},
    biburl    = {http://dblp.uni-trier.de/rec/bib/journals/corr/LiXFS16},
    bibsource = {dblp computer science bibliography, http://dblp.org}
}
```

To use this code, you will need to place your twitter credentials in common.py. If you do not have credentials or do not remember them, you can obtain them [here](https://apps.twitter.com/).

#### Get your data (easy tool)
```
python pull_star_data.py --handle <handle of broadcaster> --num_followers <how many followers you desire> --start_date YYYY-MM-DD --end_date YYYY-MM-DD --output PATH/TO/OUTPUT/<handle>.txt
```
This program will do all of the work of all the other programs, without stopping to write down the intermediary steps. Use it if you just want to get your stuff now, and don't think you'll need data like usernames. (NOTE: this takes a while to run, and if you shut down in the middle, no work will be saved! So make sure to let it finish before you stop it unless you don't care about that run).

#### Get your data (step by step)

##### Get the followers file
```
python get_followers.py --handle <username of broadcaster> --num_followers <number of followers to retrieve; default: 50> --followers_file PATH/TO/followers/<username>.txt --start_date YYYY-MM-DD --end_date YYYY-MM-DD
```
This code will produce a list of followers, as many as you specify, of the broadcaster that you specify, active between the start date and the end date (that is, they retweeted the broadcaster at least once during that time).


##### Get the tweets file

```
python get_tweets.py --handle <username of broadcaster> --followers_file PATH/TO/followers/<username>.txt --tweets_file PATH/TO/tweets/<username>.txt --start_date YYYY-MM-DD --end_date YYYY-MM-DD
```
This code will produce a csv of timestamps, usernames, and if it was a retweet, of every tweet by the broadcaster and their follower between the start date and the end date. Retweets currently are only noted if they are retweets of the original broadcaster, not across the network.


##### Postprocess the tweets file
```
python postprocessing.py --leader <username of broadcaster> --tweets_file PATH/TO/tweets/<username>.txt --processed_file PATH/TO/tweets_processed/<username>.txt
```
This code will sort the csv produced by get_tweets.py by timestamps, (and strip the username data out, using arbitrary node ids instead). A node id of 0 is used to indicate that a tweet was not a retweet, and a node id of 1 indicates the user referred to is the broadcaster.
