import os

from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
import logging
import cgi

from paypal.products import ExpressCheckout as EC
from Product import Product
from handlers.AppHandler import AppHandler

class PaymentHandler(webapp.RequestHandler):

  def post(self, mode=""):

    if mode == "set_ec":

      sid = self.request.get("sid")
      user_info = memcache.get(sid)

      product = Product.getProduct()

      nvp_params = {
              'PAYMENTREQUEST_0_AMT' : str(product['price']),
              'RETURNURL' : self.request.host_url+"/get_ec_details?sid="+sid,
              'CANCELURL': self.request.host_url+"/cancel_ec?sid="+sid
            }

      response = EC.set_express_checkout(nvp_params)

      if response.status_code != 200:
        logging.error("Failure for SetExpressCheckout")

        template_values = {
          'title' : 'Error',
          'operation' : 'SetExpressCheckout'
        }
        
        path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'unknown_error.html')
        return self.response.out.write(template.render(path, template_values))

      # Redirect to PayPal and allow user to confirm payment details.
      # Then PayPal redirects back to the /get_ec_details or /cancel_ec endpoints.
      # Assuming /get_ec_details, we complete the transaction with PayPal.get_express_checkout_details
      # and PayPal.do_express_checkout_payment

      parsed_qs = cgi.parse_qs(response.content)

      redirect_url = EC.generate_express_checkout_redirect_url(parsed_qs['TOKEN'][0])
      return self.redirect(redirect_url)

    else:
      logging.error("Unknown mode for POST request!")

  def get(self, mode=""):

    if mode == "get_ec_details":
      response = EC.get_express_checkout_details(self.request.get("token"))

      if response.status_code != 200:
        logging.error("Failure for GetExpressCheckoutDetails")

        template_values = {
          'title' : 'Error',
          'operation' : 'GetExpressCheckoutDetails'
        }
        
        path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'unknown_error.html')
        return self.response.out.write(template.render(path, template_values))

      product = Product.getProduct()

      parsed_qs = cgi.parse_qs(response.content)

      template_values = {
        'title' : 'Confirm Purchase',
        'quantity' : product['quantity'], 
        'units' : product['units'], 
        'email' : parsed_qs['EMAIL'][0], 
        'amount' : parsed_qs['PAYMENTREQUEST_0_AMT'][0],
        'query_string_params' : self.request.query_string
      }

      path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'confirm_purchase.html')
      self.response.out.write(template.render(path, template_values))

    elif mode == "do_ec_payment":

      if memcache.get(self.request.get("sid")) is not None: # Without an account reference, we can't credit the purchase
        payerid = self.request.get("PayerID")

        product = Product.getProduct()

        nvp_params = { 
                'PAYERID' : payerid, 
                'PAYMENTREQUEST_0_AMT' : str(product['price'])
        }

        response = EC.do_express_checkout_payment(
                        self.request.get("token"), 
                        nvp_params
                   )

        if response.status_code != 200:
          logging.error("Failure for DoExpressCheckoutPayment")

          template_values = {
            'title' : 'Error',
            'operation' : 'DoExpressCheckoutPayment'
          }
        
          path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'unknown_error.html')
          return self.response.out.write(template.render(path, template_values))


        # Ensure that the payment was successful
  
        parsed_qs = cgi.parse_qs(response.content)

        if parsed_qs['ACK'][0] != 'Success': 
          logging.error("Unsuccessful DoExpressCheckoutPayment")
  
          template_values = {
            'title' : 'Error',
            'details' : parsed_qs['L_LONGMESSAGE0'][0]
          }
        
          path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'unsuccessful_payment.html')
          return self.response.out.write(template.render(path, template_values))

        if parsed_qs['PAYMENTINFO_0_PAYMENTSTATUS'][0] != 'Completed': # Probably an eCheck
          logging.error("Unsuccessful DoExpressCheckoutPayment")
          logging.error(parsed_qs)
  
          template_values = {
            'title' : 'Error',
            'details' : 'Sorry, eChecks are not accepted. Please send an instant payment.'
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
        logging.error("Invalid/expired session in /do_ec_payment")

        template_values = {
          'title' : 'Session Expired',
        }

        path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'session_expired.html')
        self.response.out.write(template.render(path, template_values))

    elif mode == "cancel_ec":
      template_values = {
        'title' : 'Cancel Purchase',
      }

      path = os.path.join(os.path.dirname(__file__), '..', 'templates', 'cancel_purchase.html')
      self.response.out.write(template.render(path, template_values))
