#!/usr/bin/env/python

# Twitter authentication credentials

APP_KEY = '<App Key ("Consumer Key") goes here>'
ACCESS_TOKEN = 'Access token (see below) goes here>'

# use like so: twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)

# In order to get an access token, use the following code

APP_SECRET = '<App Secret ("Consumer Secret") goes here>'

twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
ACCESS_TOKEN = twitter.obtain_access_token()

with open("token.txt", 'wb') as output:
    output.write(ACCESS_TOKEN + "\n")

# You will find the access token written in a file "token.txt"
# in the folder you run this code in