# PaymentHandler provides logic for interacting wtih PayPal's ExpressCheckout product
# This class is invoked when the user runs out of tokens and interaction with PayPal
# is necessary. During the "normal flow" of the application, this class isn't invoked.

import os

from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
from django.utils import simplejson as json
import logging

from paypal.products import AdaptivePayment as AP
from paypal.paypal_config import seller_email as SELLER_EMAIL
from Product import Product
from handlers.AppHandler import AppHandler

class PaymentHandler(webapp.RequestHandler):

  def post(self, mode=""):

    if mode == "pay":

      sid = self.request.get("sid")

      returnUrl = self.request.host_url+"/completed_payment?sid="+sid,
      cancelUrl = self.request.host_url+"/cancelled_payment?sid="+sid

      product = Product.getProduct()

      seller = {'email' : SELLER_EMAIL, 'amount' : product['price']}

      response = AP.pay(receiver=[seller], cancelUrl=cancelUrl, returnUrl=returnUrl)
      result = json.loads(response.content)
      logging.info(result)

      if result['responseEnvelope']['ack'] == 'Failure':
        logging.error("Failure for Pay")

        template_values = {
          'title' : 'Error',
          'operation' : 'Pay'
        }
        
        path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'unknown_error.html')
        return self.response.out.write(template.render(path, template_values))

      # Stash away the payKey for later use 

      user_info = memcache.get(sid)
      user_info['payKey'] = result['payKey']
      memcache.set(sid, user_info, time=60*10) # seconds

      # Redirect to PayPal and allow user to confirm payment details.

      redirect_url = AP.generate_adaptive_payment_redirect_url(result['payKey'])
      return self.redirect(redirect_url)

    else:
      logging.error("Unknown mode for POST request!")

  def get(self, mode=""):

    if mode == "completed_payment":

      if memcache.get(self.request.get("sid")) is not None: # Without an account reference, we can't credit the purchase
        user_info = memcache.get(self.request.get("sid"))

        payKey = user_info["payKey"]

        response = AP.get_payment_details(payKey)
        result = json.loads(response.content)
        logging.info(result)

        if result['responseEnvelope']['ack'] == 'Failure' or \
           result['status'] != 'COMPLETED': # Something went wrong!

          logging.error("Failure for PaymentDetails")

          template_values = {
            'title' : 'Error',
            'operation' : 'ExecutePayment'
          }
        
          path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'unknown_error.html')
          return self.response.out.write(template.render(path, template_values))


        if result['paymentInfoList']['paymentInfo'][0]['transactionStatus'] != 'COMPLETED': # An eCheck?

          logging.error("Payment transaction status is not complete!")

          template_values = {
            'title' : 'Error',
            'details' : 'Sorry, eChecks are not accepted. Please send an instant payment.'
          }
        
          path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'unsuccessful_payment.html')
          return self.response.out.write(template.render(path, template_values))


        # Credit the user's account

        twitter_username = user_info['username']
        product = Product.getProduct()

        AppHandler.creditUserAccount(twitter_username, product['quantity'])

        template_values = {
          'title' : 'Successful Payment',
          'quantity' : product['quantity'],
          'units' : product['units']
        }
        
        path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'successful_payment.html')
        self.response.out.write(template.render(path, template_values))

      else:
        logging.error("Invalid/expired session in /completed_payment")

        template_values = {
          'title' : 'Session Expired',
        }

        path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'session_expired.html')
        self.response.out.write(template.render(path, template_values))

    elif mode == "cancelled_payment":
      template_values = {
        'title' : 'Cancel Purchase',
      }

      path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'cancel_purchase.html')
      self.response.out.write(template.render(path, template_values))
