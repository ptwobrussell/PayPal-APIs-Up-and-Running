#!/usr/bin/env python

"""
A minimal GAE application that makes an Adaptive API request to PayPal
and parses the result. Fill in your own 3 Token Credentials and sample
account information from your own sandbox account
"""

import random

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from google.appengine.api import memcache
from django.utils import simplejson as json


# Replace these values with your own 3-Token credentials and sample receivers
# who collect the funds to run this sample code in the developer sandbox

user_id = "XXX"
password = "XXX"
signature = "XXX"
receiver1, amount1 = "XXX", 10.00
receiver2, amount2 = "XXX", 5.00
receiver3, amount3 = "XXX", 2.00


class MainHandler(webapp.RequestHandler):

    # Helper function to execute requests with appropriate headers
    def _request(self, url, params):

        # standard Adaptive Payments headers
        headers = {
            'X-PAYPAL-SECURITY-USERID' : user_id,
            'X-PAYPAL-SECURITY-PASSWORD' : password,
            'X-PAYPAL-SECURITY-SIGNATURE' : signature,
            'X-PAYPAL-REQUEST-DATA-FORMAT' : 'JSON',
            'X-PAYPAL-RESPONSE-DATA-FORMAT' : 'JSON',
            'X-PAYPAL-APPLICATION-ID' : 'APP-80W284485P519543T'
        }
 
        return urlfetch.fetch(
                url,  
                payload = json.dumps(params),
                method=urlfetch.POST,
                validate_certificate=True,
                deadline=10, # seconds
                headers=headers
               )

    def get(self, mode=""):

        # /status - executes PaymentDetails when PayPal redirects back to this app after payment approval

        if mode == "status":

            payKey = memcache.get(self.request.get('sid'))

            params = {
                'requestEnvelope' : {'errorLanguage' : 'en_US', 'detailLevel' : 'ReturnAll'},
                'payKey' : payKey
            }

            result = self._request('https://svcs.sandbox.paypal.com/AdaptivePayments/PaymentDetails', params)

            response = json.loads(result.content)

            if result.status_code == 200: # OK

                # Convert back to indented JSON and display it

                pretty_json = json.dumps(response,indent=2)
                self.response.out.write('<pre>%s</pre>' % (pretty_json,))
            else:
                self.response.out.write('<pre>%s</pre>' % (json.dumps(response,indent=2),))

        else: # / (application root) - executed when app loads and initiates a Pay request

            # A cheap session implementation that's leveraged in order to lookup the payKey
            # from the Pay API and execute PaymentDetails when PayPal redirects back to /status

            sid = str(random.random())[5:] + str(random.random())[5:] + str(random.random())[5:]

            return_url = self.request.host_url + "/status" + "?sid=" + sid
            cancel_url = return_url

            redirect_url = "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_ap-payment&paykey="

            params = {
                    'requestEnvelope' : {'errorLanguage' : 'en_US', 'detailLevel' : 'ReturnAll'},
                    'actionType' : 'PAY',
                    'receiverList' : {
                            'receiver' : [
                                {'email' : receiver1, 'amount' : amount1, 'primary' : True },
                                {'email' : receiver2, 'amount' : amount2, 'primary' : False},
                                {'email' : receiver3, 'amount' : amount2, 'primary' : False}
                            ],
                    },
                'currencyCode' : 'USD',
                'memo' : 'Chained payment example.',
                'cancelUrl' : cancel_url,
                'returnUrl' : return_url,
            }

            result = self._request('https://svcs.sandbox.paypal.com/AdaptivePayments/Pay', params)
           
            response = json.loads(result.content)

            if result.status_code == 200: # OK

                # Convert back to indented JSON and inject a hyperlink to kick off payment approval

                pretty_json = json.dumps(response,indent=2)
                pretty_json = pretty_json.replace(response['payKey'], '<a href="%s%s" target="_blank">%s</a>' % (redirect_url, response['payKey'], response['payKey'],))

                memcache.set(sid, response['payKey'], time=60*10) # seconds

                self.response.out.write('<pre>%s</pre>' % (pretty_json,))
            else:
                self.response.out.write('<pre>%s</pre>' % (json.dumps(response,indent=2),))

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/(status)', MainHandler)],
                                         debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
