#!/usr/bin/env python

"""
A minimal GAE application that makes an API request to PayPal
and parses the result. Fill in your own 3 Token Credentials
from your sandbox account
"""

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch

import urllib
import cgi

class MainHandler(webapp.RequestHandler):
    def get(self):

        # Sandbox NVP API endpoint

        sandbox_api_url = 'https://api-3t.sandbox.paypal.com/nvp'

        nvp_params = {
            # 3 Token Credentials

            'USER' : 'XXX',
            'PWD' : 'XXX',
            'SIGNATURE' : 'XXX',

            # API Version and Operation

            'METHOD' : 'SetExpressCheckout',
            'VERSION' : '82.0',

            # API specifics for SetExpressCheckout

            'PAYMENTREQUEST_0_AMT' : '1.00',
            'RETURNURL' : 'http://ppapis2e.appspot.com/xxx_returnurl_xxx',
            'CANCELURL' : 'http://ppapis2e.appspot.com/xxx_cancelurl_xxx'
        }

        # Make a secure request and pass in nvp_params as a POST payload

        result = urlfetch.fetch(
                    sandbox_api_url,  
                    payload = urllib.urlencode(nvp_params),
                    method=urlfetch.POST,
                    validate_certificate=True
                 )

        if result.status_code == 200: # OK

            decoded_url = cgi.parse_qs(result.content)

            for (k,v) in decoded_url.items():
                self.response.out.write('<pre>%s=%s</pre>' % (k,v[0],))
        else:

            self.response.out.write('Could not fetch %s (%i)' % 
                    (url, result.status_code,))

def main():
    application = webapp.WSGIApplication([('/', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
