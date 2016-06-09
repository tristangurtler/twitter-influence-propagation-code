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

#### Get the followers file
```
python get_followers.py --handle <username of broadcaster> --num_followers <number of followers to retrieve; default: 50> --followers_file PATH/TO/followers/<username>.txt --start_date YYYY-MM-DD --end_date YYYY-MM-DD
```


#### Get the tweets file

```
python get_tweets.py --handle <username of broadcaster> --followers_file PATH/TO/followers/<username>.txt --tweets_file PATH/TO/tweets/<username>.txt --start_date YYYY-MM-DD --end_date YYYY-MM-DD
```


#### Postprocess the tweets file
```
python postprocessing.py --leader <username of broadcaster> --tweets_file PATH/TO/tweets/<username>.txt --processed_file PATH/TO/tweets_processed/<username>.txt
```
