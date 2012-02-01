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
              'L_PAYMENTREQUEST_0_NAME0' : str(product['quantity']) + ' ' + product['units'],
              'L_PAYMENTREQUEST_0_AMT0' : str(product['price']),
              'L_PAYMENTREQUEST_0_QTY0' : 1,
              'L_PAYMENTREQUEST_0_ITEMCATEGORY0' : 'Digital',

              'PAYMENTREQUEST_0_AMT' : str(product['price']),
              'RETURNURL' : self.request.host_url+"/do_ec_payment?sid="+sid,
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

      # The remainder of the transaction is completed in context

      parsed_qs = cgi.parse_qs(response.content)

      redirect_url = EC.generate_express_checkout_digital_goods_redirect_url(parsed_qs['TOKEN'][0])
      return self.redirect(redirect_url)

    else:
      logging.error("Unknown mode for POST request!")

  def get(self, mode=""):

    if mode == "do_ec_payment":

      if memcache.get(self.request.get("sid")) is not None: # Without an account reference, we can't credit the purchase
        payerid = self.request.get("PayerID")

        product = Product.getProduct()

        nvp_params = { 
                'PAYERID' : payerid, 

                'L_PAYMENTREQUEST_0_NAME0' : str(product['quantity']) + ' ' + product['units'],
                'L_PAYMENTREQUEST_0_AMT0' : str(product['price']),
                'L_PAYMENTREQUEST_0_QTY0' : 1,
                'L_PAYMENTREQUEST_0_ITEMCATEGORY0' : 'Digital',

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

        if parsed_qs['PAYMENTINFO_0_PAYMENTSTATUS'][0] != 'Completed':
          logging.error("Unsuccessful DoExpressCheckoutPayment")
          logging.error(parsed_qs)
  
          template_values = {
            'title' : 'Error',
            'details' : 'Sorry, but there was an unexpected problem processing your payment.'
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
