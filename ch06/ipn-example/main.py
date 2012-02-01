#!/usr/bin/env python

# Use the IPN Simulator from the "Test Tools" at developer.paypal.com to
# send this app an IPN. This app must be deployed to the live GAE environment
# for the PayPal IPN Simulator to address it. When debugging, it's a necessity
# to use logging messages and view them from the GAE Dashboard's Logs pane.

# You can also login to a Sandbox Merchant account and set the IPN URL for
# this app under the Merchant Profile tab.

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.api import urlfetch
from google.appengine.api import mail
import cgi

import logging

# In production, gae_email_sender must be an authorized account that's been
# added to the GAE Dashboard under Administration/Permissions or else you
# won't be able to send mail. You can use the default owner of the account
# or add/verify additional addresses

gae_email_sender = "XXX"
ipn_sandbox_url = "https://www.sandbox.paypal.com/cgi-bin/webscr"

class IPNHandler(webapp.RequestHandler):

    @staticmethod
    def sendMail(first_name, last_name, email, debug_msg=None, bcc=None):
        message = mail.EmailMessage(sender="Customer Support <%s>" % (gae_email_sender,),
                                    subject="Your recent purchase")

        message.to = "%s %s <%s>" % (first_name, last_name, email,)

        message.body = """Dear %s:

Thank you so much for your recent purchase.

Please let us know if you have any questions.

Regards,
Customer Support""" % (first_name,)

        if debug_msg:
            message.body = message.body + '\n' + '*'*20 + '\n' + debug_msg + '\n' + '*'*20

        if bcc:
            message.bcc = bcc

        message.send()


    def post(self, mode=""):

        # PayPal posts to /ipn to send this application an IPN

        if mode == "ipn":

            logging.info(self.request.body)
           
            # To ensure that it was really PayPal that sent the IPN, we post it back
            # with a preamble and then verify that we get back VERIFIED and a 200 response

            result = urlfetch.fetch(
                        ipn_sandbox_url, 
                        payload = "cmd=_notify-validate&" + self.request.body,
                        method=urlfetch.POST,
                        validate_certificate=True
                     )

            logging.info(result.content)

            if result.status_code == 200 and result.content == 'VERIFIED': # OK

                # See pages 19-20 of the Instant Payment Notification Guide at
                # https://cms.paypal.com/cms_content/US/en_US/files/developer/IPNGuide.pdf
                # for various actions that should be taken based on the IPN values.

                ipn_values = cgi.parse_qs(self.request.body)
                debug_msg = '\n'.join(["%s=%s" % (k,'&'.join(v)) for (k,v) in ipn_values.items()])

                # The Sandbox users don't have real mailboxes, so bcc the GAE email sender as a way to
                # debug during development
                self.sendMail(ipn_values['first_name'][0], ipn_values['last_name'][0], ipn_values['payer_email'], 
                              debug_msg=debug_msg, bcc=gae_email_sender)
            else:
                logging.error('Could not fetch %s (%i)' % (url, result.status_code,))

        else:
            logging.error("Unknown mode for POST request!")

def main():
    application = webapp.WSGIApplication([('/', IPNHandler),
                                          ('/(ipn)', IPNHandler)],
                                         debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
