sandbox_api_url = 'https://api-3t.sandbox.paypal.com/nvp'

adaptive_sandbox_api_pay_url = 'https://svcs.sandbox.paypal.com/AdaptivePayments/Pay'
adaptive_sandbox_api_payment_details_url = 'https://svcs.sandbox.paypal.com/AdaptivePayments/PaymentDetails'

nvp_params = { 

    # 3 Token Credentials

    'USER' : 'XXX',
    'PWD' : 'XXX',
    'SIGNATURE' : 'XXX',

    # API Version

    'VERSION' : '82.0'
}   

adaptive_headers = {
    'X-PAYPAL-SECURITY-USERID' : 'XXX',
    'X-PAYPAL-SECURITY-PASSWORD' : 'XXX',
    'X-PAYPAL-SECURITY-SIGNATURE' : 'XXX',
    'X-PAYPAL-REQUEST-DATA-FORMAT' : 'JSON',
    'X-PAYPAL-RESPONSE-DATA-FORMAT' : 'JSON',
    'X-PAYPAL-APPLICATION-ID' : 'APP-80W284485P519543T' # Sandbox
}

seller_email = 'XXX'
