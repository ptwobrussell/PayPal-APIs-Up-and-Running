#!/usr/bin/env python

##################################################################################################
# This GAE project provides demonstrates how to create a minimal web app that authenticates 
# users with their Twitter account and displays only their most relevant tweets
# (as determined by a trivial algorithm that can easily be modified/extended) as part of a 
# UX that is optimized for a mobile client. First-time visitors get to login free for a number
# of times and experience the app before they are requested to purchase additional logins to
# continue using the app.
#
# Credits:
# 
# Mike Knapp's https://github.com/mikeknapp/AppEngine-OAuth-Library project is used to 
# handle making OAuth requests to Twitter as part of the authentication process.
#
# Pat Coll's https://github.com/patcoll/paypal-python project provided a starting point for 
# implementing an Express Checkout payment flow, but was so heavily modified that it is no
# longer recognizable.
#
# The application's primary UI is adapted from the final installment of SitePen's TweetView
# project at http://dojotoolkit.org/documentation/tutorials/1.6/mobile/tweetview/packaging/ 
# and is intended to be delivered to a mobile display like an iPhone, although development
# works fine on a desktop browser like WebKit. The UI for the payflows is minimal.
##################################################################################################

# Minimal GAE imports to run the app

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util

# Application specific logic

from handlers.AppHandler import AppHandler

# Logic for interacting with Twitter's API and serving up data, etc.

def main():
                                        
  application = webapp.WSGIApplication([

                                        # AppHandler URLs

                                        ('/(app)', AppHandler),
                                        ('/(data)', AppHandler),
                                        ('/(login)', AppHandler),
                                        ('/', AppHandler)
                                       ],

                                       debug=True)
  util.run_wsgi_app(application)

if __name__ == '__main__':
  main()
