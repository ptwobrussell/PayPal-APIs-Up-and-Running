#!/usr/bin/env python

"""
A minimal GAE application that securely fetches a URL
"""

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch

class MainHandler(webapp.RequestHandler):
    def get(self):
        url = "https://www.paypal.com/"
        result = urlfetch.fetch(
                      url,  
                      validate_certificate=True # Avoid man-in-the-middle attacks
                 )   
        if result.status_code == 200:
            self.response.out.write('Successfully fetched ' + url)
        else:
            self.response.out.write('Could not fetch %s (%i)' % (url, result.status_code,))


def main():
    application = webapp.WSGIApplication([('/', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
