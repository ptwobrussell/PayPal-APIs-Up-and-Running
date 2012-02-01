#!/bin/bash

# Replace XXX values with your own credentials

USERID="XXX"
PASSWORD="XXX"
SIGNATURE="XXX"

APPID="APP-80W284485P519543T"
RECEIVER="XXX"
AMOUNT="1.00"
CANCELURL="http://example.com/cancel"
RETURNURL="http://example.com/return"
IPNURL="http://example.com/ipn"

RESULT=$(curl -s \
-H "X-PAYPAL-SECURITY-USERID: $USERID" \
-H "X-PAYPAL-SECURITY-PASSWORD: $PASSWORD" \
-H "X-PAYPAL-SECURITY-SIGNATURE: $SIGNATURE" \
-H "X-PAYPAL-REQUEST-DATA-FORMAT: NV" \
-H "X-PAYPAL-RESPONSE-DATA-FORMAT: JSON" \
-H "X-PAYPAL-APPLICATION-ID: $APPID" \
https://svcs.sandbox.paypal.com/AdaptivePayments/Pay -d "requestEnvelope.errorLanguage=en_US\
&actionType=PAY\
&receiverList.receiver(0).email=$RECEIVER\
&receiverList.receiver(0).amount=$AMOUNT\
&currencyCode=USD\
&feesPayer=EACHRECEIVER\
&memo=Simple payment example.\
&cancelUrl=$CANCELURL\
&returnUrl=$RETURNURL\
&ipnNotificationUrl=$IPNURL"\
;)

echo $RESULT
