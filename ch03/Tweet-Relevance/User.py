from google.appengine.ext import db

# User is (conceptually) just a simple tuple to track access to the application
# No additional user information is stored in an attempt to keep this app as minimal 
# and stateless as possible. 

class User(db.Model):
  twitter_username = db.StringProperty(required=True)
  requests_remaining = db.IntegerProperty(required=True, default=25)
