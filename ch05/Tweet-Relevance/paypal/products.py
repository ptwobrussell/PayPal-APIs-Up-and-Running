from google.appengine.api import urlfetch

import urllib
import cgi

import paypal_config

class DirectPayment(object):

    @staticmethod
    def _api_call(nvp_params):

        params = nvp_params.copy()       # copy to avoid mutating nvp_params with update()
        params.update(paypal_config.nvp_params) # update with 3 token credentials and api version

        response = urlfetch.fetch(
                    paypal_config.sandbox_api_url,
                    payload=urllib.urlencode(params),
                    method=urlfetch.POST,
                    validate_certificate=True,
                    deadline=10 # seconds
                   )   

        if response.status_code != 200:
            decoded_url = cgi.parse_qs(result.content)

            for (k,v) in decoded_url.items():
                logging.error('%s=%s' % (k,v[0],))

            raise Exception(str(response.status_code))

        return response

    @staticmethod
    def do_direct_payment(nvp_params):
        nvp_params.update(METHOD='DoDirectPayment')
        nvp_params.update(PAYMENTACTION='Sale')
        return DirectPayment._api_call(nvp_params)
