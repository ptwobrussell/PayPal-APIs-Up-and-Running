# User is (conceptually) just a simple tuple to track access to the application
# No additional user information is stored in an attempt to keep this app as minimal 
# and stateless as possible. 

from google.appengine.ext import db

class User(db.Model):
  twitter_username = db.StringProperty(required=True)

  # Set to "now" the first time the instance is added to the datastore
  access_start = db.DateTimeProperty(required=True, auto_now_add=True)

  # Days
  access_duration = db.IntegerProperty(required=True, default=30)
