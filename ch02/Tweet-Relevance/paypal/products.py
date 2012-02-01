from google.appengine.api import urlfetch

import urllib
import cgi

import paypal_config

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


class ExpressCheckout(object):

    @staticmethod
    def set_express_checkout(nvp_params):
        nvp_params.update(METHOD='SetExpressCheckout')
        return _api_call(nvp_params)

    @staticmethod
    def get_express_checkout_details(token):
        nvp_params = {'METHOD' : 'GetExpressCheckoutDetails', 'TOKEN' : token}
        return _api_call(nvp_params)

    @staticmethod
    def do_express_checkout_payment(token, nvp_params):
        nvp_params.update(METHOD='DoExpressCheckoutPayment', TOKEN=token)
        return _api_call(nvp_params)
        
    @staticmethod
    def generate_express_checkout_redirect_url(token):
        return "https://www.sandbox.paypal.com/webscr?cmd=_express-checkout&token=%s" % (token,)
