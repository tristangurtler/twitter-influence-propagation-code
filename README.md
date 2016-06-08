# twitter-influence-propagation-code

Code to generate dataset used in the twitter [influence propagation work](http://arxiv.org/pdf/1603.08981v1.pdf)

```
@article{DBLP:journals/corr/LiXFS16,
    author    = {Shuang Li and
        Yao Xie and
            Mehrdad Farajtabar and
            Le Song},
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

Place your twitter credentials in common.py. You can obtain your twitter credentials from https://apps.twitter.com/

#### Get the followers file
```
python get_followers.py --handle FLOTUS --follower_file followers/FLOTUS.txt --start_date 2016-01-01 --end_date 2016-01-30
```


#### Get the tweets file

```
python get_tweets.py --handle FLOTUS --followers_file followers/FLOTUS.txt --tweets_file tweets/FLOTUS.txt --start_date 2016-01-01 --end_date 2016-01-30
```


#### Postprocess the tweets file
```
python postprocessing.py --leader_handle NASA --tweets_file tweets/NASA.txt --output tweets_processed/NASA.txt
```
