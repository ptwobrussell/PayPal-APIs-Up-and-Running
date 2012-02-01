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

# Replace these values with your own 3-Token credentials from a sandbox 
# merchant account that was configured for Website Payments Pro and a faux
# credit card number and expiry from a "personal" buyer account

user_id = "XXX"
password = "XXX"
signature = "XXX"

credit_card_number = "XXX"
credit_card_expiry ="XXX"

class MainHandler(webapp.RequestHandler):
    def get(self):

        # Sandbox NVP API endpoint

        sandbox_api_url = 'https://api-3t.sandbox.paypal.com/nvp'

        nvp_params = {
            # 3 Token Credentials

            'USER' : user_id,
            'PWD' : password,
            'SIGNATURE' : signature,

            # API Version and Operation

            'METHOD' : 'DoDirectPayment',
            'VERSION' : '82.0',

            # API specifics for DoDirectPayment
            'PAYMENTACTION' : 'Sale',
            'IPADDRESS' : '192.168.0.1',
            'AMT' : '8.88',
            'CREDITCARDTYPE' : 'Visa',
            'ACCT' : credit_card_number,
            'EXPDATE' : credit_card_expiry,
            'CVV2' : '123',
            'FIRSTNAME' : 'Billy',
            'LASTNAME' : 'Jenkins',
            'STREET' : '1000 Elm St.',
            'CITY' : 'Franklin',
            'STATE' : 'TN',
            'ZIP' : '37064',
            'COUNTRYCODE' : 'US'
        }

        # Make a secure request and pass in nvp_params as a POST payload

        result = urlfetch.fetch(
                    sandbox_api_url,  
                    payload = urllib.urlencode(nvp_params),
                    method=urlfetch.POST,
                    deadline=10, # seconds
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
