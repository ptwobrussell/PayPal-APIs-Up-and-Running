from google.appengine.api import urlfetch
from django.utils import simplejson as json

import urllib
import cgi

import paypal_config

class AdaptivePayment(object):

    @staticmethod
    def _api_call(url, params):

        response = urlfetch.fetch(
                    url,
                    payload=json.dumps(params),
                    method=urlfetch.POST,
                    validate_certificate=True,
                    deadline=10, # seconds
                    headers=paypal_config.adaptive_headers
                   )   

        if response.status_code != 200:
            result = json.loads(response.content)
            logging.error(json.dumps(response.content, indent=2))

            raise Exception(str(response.status_code))

        return response


    # Lists out some of the most common parameters as keyword args. Other keyword args can be added through kw as needed
    # Template for an item in the receiver list: {'email' : me@example.com, 'amount' : 1.00, 'primary' : False}

    @staticmethod
    def pay(sender=None, receiver=[], feesPayer='EACHRECEIVER', memo='', cancelUrl='', returnUrl='', **kw ):

        params = {
            'requestEnvelope' : {'errorLanguage' : 'en_US', 'detailLevel' : 'ReturnAll'},
            'actionType' : 'PAY',
            'currencyCode' : 'USD',
            'senderEmail' : sender,
            'receiverList' : {
                    'receiver' : receiver
            },
            'feesPayer' : feesPayer,
            'memo' : memo,
            'cancelUrl' : cancelUrl,
            'returnUrl' : returnUrl 
        }

        if sender is None: params.pop('senderEmail')

        if memo == "": params.pop('memo')

        params.update(kw)

        return AdaptivePayment._api_call(paypal_config.adaptive_sandbox_api_pay_url, params)

    @staticmethod
    def get_payment_details(payKey):

        params = {
            'requestEnvelope' : {'errorLanguage' : 'en_US', 'detailLevel' : 'ReturnAll'},
            'payKey' : payKey
        }

        return AdaptivePayment._api_call(paypal_config.adaptive_sandbox_api_payment_details_url, params)

    @staticmethod
    def generate_adaptive_payment_redirect_url(payKey, embedded=False):
        if embedded:
            return "https://www.sandbox.paypal.com/webapps/adaptivepayment/flow/pay?payKey=%s" % (payKey,)
        else:
            return "https://www.sandbox.paypal.com/cgi-bin/webscr?cmd=_ap-payment&paykey=%s" % (payKey,)
