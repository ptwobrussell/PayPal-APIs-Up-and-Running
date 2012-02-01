from google.appengine.ext import db

# User is a simple (twitter_username, requests_remaining) tuple to track logins so that users
# can be charged for access. By default, users get 25 free logins. No additional user information
# is stored in an attempt to keep this app as minimal and stateless as possible. (And memcache is
# used to implement a minimalist session management scheme to keep track of the user between
# requests.)

class User(db.Model):
  twitter_username = db.StringProperty(required=True)
  requests_remaining = db.IntegerProperty(required=True, default=25)
