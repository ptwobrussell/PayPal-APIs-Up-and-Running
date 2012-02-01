#!/bin/bash

# Replace XXX values with your own credentials

# Ensure that the 3-Token credentials are with a business account that has explicitly
# been configured for Website Payments Pro at http://developer.paypal.com

USER="XXX"
PWD="XXX"
SIGNATURE="XXX"

# Ensure that the credit card used is a real credit card number from an account
# that has been configured at http://developer.paypal.com 
# The sandbox environment does require that the credit card number and expiry
# be valid

ACCT="XXX"
EXPDATE="XXX"

RESULT=$(curl -s \
https://api-3t.sandbox.paypal.com/nvp -d "VERSION=82.0\
&USER=$USER\
&PWD=$PWD\
&SIGNATURE=$SIGNATURE\
&METHOD=DoDirectPayment\
&PAYMENTACTION=Sale\
&IPADDRESS=192.168.0.1\
&AMT=8.88\
&CREDITCARDTYPE=Visa\
&ACCT=$ACCT\
&EXPDATE=$EXPDATE\
&CVV2=123\
&FIRSTNAME=Billy\
&LASTNAME=Jenkins\
&STREET=1000 Elm St.\
&CITY=Franklin\
&STATE=TN\
&ZIP=37064\
&COUNTRYCODE=US"\
;)

echo $RESULT;
