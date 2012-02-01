# PaymentHandler provides logic for interacting wtih PayPal's Website Payments Pro product

import os
import cgi

from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
import logging

from paypal.products import DirectPayment as DP
from Product import Product
from handlers.AppHandler import AppHandler


class PaymentHandler(webapp.RequestHandler):

  def post(self, mode=""):

    if mode == "do_direct_payment":

     # To be on the safe side, filter through a pre-defined list of fields
     # to pass through to DoDirectPayment. i.e. prevent the client from
     # potentially overriding IPADDRESS, AMT, etc.

      valid_fields = [
          'FIRSTNAME',
          'LASTNAME',
          'STREET',
          'CITY',
          'STATE',
          'ZIP',
          'COUNTRYCODE',
          'CREDITCARDTYPE',
          'ACCT',
          'EXPDATE',
          'CVV2',
      ]
      
      product = Product.getProduct()

      nvp_params = {'AMT' : str(product['price']), 'IPADDRESS' : self.request.remote_addr}

      for field in valid_fields:
        nvp_params[field] = self.request.get(field)

      response = DP.do_direct_payment(nvp_params)

      if response.status_code != 200:
        logging.error("Failure for DoDirectPayment")

        template_values = {
          'title' : 'Error',
          'operation' : 'DoDirectPayment'
        }
        
        path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'unknown_error.html')
        return self.response.out.write(template.render(path, template_values))

      # Ensure that the payment was successful

      parsed_qs = cgi.parse_qs(response.content)

      if parsed_qs['ACK'][0] != 'Success':
        logging.error("Unsuccessful DoDirectPayment")

        template_values = {
          'title' : 'Error',
          'details' : parsed_qs['L_LONGMESSAGE0'][0]
        }
        
        path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'unsuccessful_payment.html')
        return self.response.out.write(template.render(path, template_values))


      # Credit the user's account

      user_info = memcache.get(self.request.get("sid"))
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
      logging.error("Unknown mode for POST request!")
