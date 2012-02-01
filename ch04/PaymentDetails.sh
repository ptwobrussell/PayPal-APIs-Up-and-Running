#!/bin/bash

PAYKEY="${1}"

# Replace XXX values with your own credentials

USERID="XXX"
PASSWORD="XXX"
SIGNATURE="XXX"

APPID="APP-80W284485P519543T"

RESULT=$(curl -s \
-H "X-PAYPAL-SECURITY-USERID: $USERID" \
-H "X-PAYPAL-SECURITY-PASSWORD: $PASSWORD" \
-H "X-PAYPAL-SECURITY-SIGNATURE: $SIGNATURE" \
-H "X-PAYPAL-REQUEST-DATA-FORMAT: NV" \
-H "X-PAYPAL-RESPONSE-DATA-FORMAT: JSON" \
-H "X-PAYPAL-APPLICATION-ID: $APPID" \
https://svcs.sandbox.paypal.com/AdaptivePayments/PaymentDetails -d "requestEnvelope.errorLanguage=en_US\
&payKey=$PAYKEY"\
;)

echo $RESULT
